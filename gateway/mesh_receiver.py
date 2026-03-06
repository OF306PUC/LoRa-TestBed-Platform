import time
from datetime import datetime, timezone
import meshtastic
import meshtastic.serial_interface
from pubsub import pub

from mqtt_connector import MQTTConnector


class MeshReceiver:
    """
    Connects to the local Meshtastic gateway over serial, listens for
    telemetry packets from known nodes, and publishes them to MQTT.
    """

    SEEN_MAX = 50

    def __init__(self, mqtt: MQTTConnector, known_nodes: dict):
        """
        Args:
            mqtt (MQTTConnector): Connected MQTT client for publishing.
            known_nodes (dict): Map of node_id -> label, e.g. {"!0b64122b": "node-1"}.
        """
        self.mqtt        = mqtt
        self.known_nodes = known_nodes
        self.seen_ids    = set()
        self.iface       = None
        self.my_id       = None
        self.my_num      = None

    def connect(self):
        """Opens the serial connection to the Meshtastic gateway."""
        self.iface  = meshtastic.serial_interface.SerialInterface()
        me          = self.iface.getMyNodeInfo()
        self.my_id  = me["user"]["id"]
        self.my_num = me["num"]
        print(f"[MESH] Gateway node: {self.my_id} (num={self.my_num})")
        print(f"[MESH] Watching nodes: {list(self.known_nodes.keys())}\n")

    def listen(self):
        """Subscribes to incoming packets and blocks until KeyboardInterrupt."""
        pub.subscribe(self._on_receive, "meshtastic.receive")
        print("Listening... Ctrl+C to stop.\n")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.close()

    def close(self):
        """Closes serial and MQTT connections cleanly."""
        print("\n[MESH] Shutting down...")
        if self.iface:
            self.iface.close()
        self.mqtt.close()

    # ── Packet handling ───────────────────────────────────────────────────────

    def _on_receive(self, packet, interface):
        if not packet or "decoded" not in packet:
            return

        sender_id  = packet.get("fromId")
        sender_num = packet.get("from")

        if not self._is_valid(sender_id, sender_num, packet.get("id")):
            print(f"[MESH] Dropping packet from {sender_id} (num={sender_num})")
            return

        decoded = packet["decoded"]
        if decoded.get("portnum") != "TELEMETRY_APP":
            return

        label       = self.known_nodes[sender_id]
        telem       = decoded.get("telemetry", {})
        print(f"\nTelemetry from {sender_id or sender_num}: {telem}")
        device_ts   = telem.get("time", int(time.time()))
        received_at = datetime.now(timezone.utc).isoformat()

        self._handle_device_telemetry(sender_id, label, telem, device_ts, received_at)
        self._handle_env_telemetry(sender_id, label, telem, device_ts, received_at)

    def _is_valid(self, sender_id: str, sender_num: int, packet_id) -> bool:
        """Returns False if the packet should be dropped."""
        if sender_id == self.my_id or sender_num == self.my_num:
            return False
        if sender_id not in self.known_nodes:
            return False
        if packet_id is not None:
            if packet_id in self.seen_ids:
                return False
            self.seen_ids.add(packet_id)
            if len(self.seen_ids) > self.SEEN_MAX:
                self.seen_ids.clear()
        return True

    # ── Telemetry parsers ─────────────────────────────────────────────────────

    def _handle_device_telemetry(self, node_id: str, label: str, telem: dict, device_ts: int, received_at: str):
        device = telem.get("deviceMetrics", {})
        if not device:
            return

        payload = {
            "node_id":        node_id,
            "node_label":     label,
            "device_ts":      device_ts,
            "received_at":    received_at,
            "battery_level":  device.get("batteryLevel"),
            "voltage":        device.get("voltage"),
            "channel_util":   device.get("channelUtilization"),
            "air_util_tx":    device.get("airUtilTx"),
            "uptime_seconds": device.get("uptimeSeconds"),
            "usb_power":      device.get("usbPower"),
            "is_charging":    device.get("isCharging"),
        }

        print(f"\n[DEVICE] {label} ({node_id})")
        print(f"    device_ts:   {device_ts}")
        print(f"    received_at: {received_at}")
        for k, v in payload.items():
            if k not in ("node_id", "node_label", "device_ts", "received_at"):
                print(f"    {k}: {v}")

        self.mqtt.publish_device(label, payload)

    def _handle_env_telemetry(self, node_id: str, label: str, telem: dict, device_ts: int, received_at: str):
        env = telem.get("environmentMetrics", {})
        if not env:
            return

        payload = {
            "node_id":     node_id,
            "node_label":  label,
            "device_ts":   device_ts,
            "received_at": received_at,
            "temperature": env.get("temperature"),
            "humidity":    env.get("relativeHumidity"),
            "pressure":    env.get("barometricPressure"),
        }

        print(f"\n[ENV] {label} ({node_id})")
        print(f"    device_ts:   {device_ts}")
        print(f"    received_at: {received_at}")
        for k, v in payload.items():
            if k not in ("node_id", "node_label", "device_ts", "received_at"):
                print(f"    {k}: {v}")

        self.mqtt.publish_env(label, payload)