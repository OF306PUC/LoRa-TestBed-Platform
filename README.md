# 🌿 LoRa TestBed Platform

> An early-stage environmental monitoring platform built on LoRa mesh networking and Meshtastic firmware, using solar-powered nodes and a USB-connected gateway.

**Cyber-Physical Systems Research and Technology Center**
[Pontificia Universidad Católica de Chile](https://www.uc.cl)

---

## Overview

This project establishes a LoRa mesh network for environmental monitoring — capturing **temperature, humidity, power metrics, and GPS data** from remote solar-powered nodes. Configuration and control are handled through Python scripts that interface with the [Meshtastic](https://meshtastic.org/) CLI, without modifying the underlying firmware.

The network consists of **3 SensCAP Solar Node P1 Pro sensor nodes** and **1 LILYGO gateway board**, connected via USB to a WiFi-enabled host computer.

---

## Hardware

| Component | Role | Details |
|---|---|---|
| **Seeed Studio SensCAP Solar Node P1 Pro** (×3) | Sensor Nodes | Solar-powered LoRa nodes; temperature & humidity sensing |
| **LILYGO Board** (×1) | Gateway | USB-connected to host; WiFi-enabled |
| **Host Computer** | Control Hub | Runs Python scripts; WiFi access for data forwarding |

### Node Architecture

![SensCAP Node Architecture](docs/sensecap-node.drawio.png)

### Gateway Architecture
![Gateway LILYGO Architecture](docs/gateway.drawio.png)

### Mesh Network Topology

![Mesh Network Graph](docs/sensecap-mesh-mesh.drawio.png)

---

## Repository Structure

```
LoRa-TestBed-Platform/
│
├── UF2/
│   ├── erase_firmware/           # UF2 binary to erase existing firmware (nRF52)
│   └── upload_firmware/          # Meshtastic UF2 firmware binary for SensCAP nodes
│
├── docs/                         # Documentation and reference diagrams
│
├── gateway/                      # Gateway-specific configuration
│   ├── param_receiver.py         # Parameters for the LILYGO gateway
│   ├── receiver-config.py        # Script to configure the gateway via Meshtastic CLI
│   └── receiver_config.yaml      # Reference YAML config for the gateway
│
├── node-config.py                # Configures sensor nodes via Meshtastic CLI
├── param_node.py                 # Shared parameters and constants for sensor nodes
├── check-node-info.py            # Utility: reads and prints node info over serial
│
├── config.yaml                   # Reference YAML config for sensor nodes
├── firmware_inital_config.yaml   # Initial firmware configuration (pre-channel setup)
├── mesh_config.json              # Per-node mesh parameters (roles, hop limits, IDs)
├── requirements.txt              # Python dependencies
│
├── mqtt/
│   └── mosquitto.conf            # Mosquitto broker configuration
│
├── telegraf/
│   └── etc/telegraf.conf         # Telegraf agent configuration (MQTT → InfluxDB)
│
├── docker-compose.yaml           # Container orchestration
├── configuration.env             # InfluxDB environment variables
│
└── README.md
```

---

## File Descriptions

### `param_node.py` — Sensor Node Parameters

Centralises all configurable constants for the sensor node configuration script:

- **Channel settings** — channel index, name (`TB CPS-RTC`), and PSK key (base64-encoded)
- **LoRa radio settings** — region (`ANZ`) and modem preset (`MEDIUM_FAST`)
- **Rebroadcast mode** — set to `LOCAL_ONLY` to isolate the mesh from foreign traffic
- **Telemetry intervals** — environment measurements every `120` seconds; device metrics on demand
- **Solar Node Device roles** — `CLIENT` or `SENSOR`
- **Hop limit** — computed as `REQUIRED_HOPS_TO_GATEWAY + 1`; must be set per node
- **GPS settings** — GPS reporting every `300` seconds

### `node-config.py` — Sensor Node Configuration Script

Configures a single sensor node via the Meshtastic CLI. Run once per node, passing the node ID as an argument. Applies settings in this order:

1. Sets LoRa region and modem preset
2. Sets the hop limit (loaded from `mesh_config.json` per node)
3. Sets rebroadcast mode to `LOCAL_ONLY`
4. Configures the private mesh channel (name + PSK)
5. Sets the device role (`CLIENT` or `SENSOR`)
6. Enables environment telemetry and sets update intervals
7. Sets GPS update interval
8. Reboots the node to apply all changes

**Usage:**
```bash
python node-config.py --node-id <ID>
```

For example, to configure node 1:
```bash
python node-config.py --node-id 1
```

### `gateway/receiver-config.py` — Gateway Configuration Script

Configures the LILYGO gateway node. Uses parameters from `gateway/param_receiver.py`. The gateway is configured with role `CLIENT_MUTE` (receives mesh traffic but does not rebroadcast), with telemetry and GPS disabled since it only acts as a data sink.

**Usage:**
```bash
cd gateway
python receiver-config.py
```

### `check-node-info.py` — Node Inspection Utility

Connects to a node over serial and prints its current node info. Useful for verifying that a node is reachable and has been configured correctly.

**Usage:**
```bash
python check-node-info.py
```

### `mesh_config.json` — Per-Node Mesh Parameters

Defines each node's hardware ID, `device_role`, and `hop_limit`. Referenced at runtime by `node-config.py`.

```json
{
  "nodes_cfg": {
    "1": {"id": "!0b64122b", "hop_limit": 3, "device_role": "SENSOR"},
    "2": {"id": "!6c73ff1c", "hop_limit": 2, "device_role": "CLIENT"},
    "3": {"id": "!9d84gg2d", "hop_limit": 2, "device_role": "CLIENT"}
  }
}
```

### `firmware_inital_config.yaml` / `config.yaml`

YAML reference configs for initial device setup and post-channel configuration respectively. Can be applied directly using the Meshtastic CLI's `--configure` flag.

---

## Getting Started

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- LILYGO gateway and all sensor nodes connected via USB (one at a time during configuration)
- Meshtastic Python CLI (installed via `requirements.txt`)

### Installation

```bash
# Clone the repository
git clone https://github.com/OF306PUC/LoRa-TestBed-Platform.git
cd LoRa-TestBed-Platform

# Create virtual environment (Linux)
python3 -m venv .venv

# Install dependencies
source .venv/bin/activate
pip install -r requirements.txt
```

---

### Step 1 — Flash Meshtastic Firmware ⚡ *(Required before any Python configuration)*

> **This step must be completed on every sensor node before running any configuration scripts.**
> The Meshtastic CLI communicates with devices over USB serial — the scripts will not work on a device that has not been flashed with Meshtastic firmware.

The `UF2/` folder contains the firmware binaries for the SensCAP Solar Node P1 Pro (nRF52-based). The UF2 method requires no additional tools — it works via drag-and-drop.

#### 1a — Erase existing firmware (recommended for new or re-used devices)

1. Connect the device via USB.
2. Double-press the reset button to enter bootloader mode — the device appears as a USB drive.
3. Drag and drop `UF2/erase_firmware/nrf_erase_sd7_3.uf2` onto the drive.
4. The device will reboot and the drive will reappear — it is now erased.

#### 1b — Flash Meshtastic firmware

1. With the device still in bootloader mode (double-press reset again if needed), drag and drop `UF2/upload_firmware/firmware-seeed_solar_node-2.7.19.bb3d6d5.uf2` onto the drive.
2. The device will reboot automatically once flashing is complete.
3. Repeat Steps 1a and 1b for **all 3 sensor nodes**.

> ℹ️ The LILYGO gateway uses a different flashing method. Refer to the [Meshtastic flashing documentation](https://meshtastic.org/docs/getting-started/flashing-firmware/) for ESP32-based boards.

👉 Full nRF52 flashing reference: [Meshtastic UF2 Drag-and-Drop Flashing Guide](https://meshtastic.org/docs/getting-started/flashing-firmware/nrf52/drag-n-drop/)

---

### Step 2 — Configure the Gateway

Connect the LILYGO gateway via USB, then run:

```bash
cd gateway
python receiver-config.py
```

This applies the `CLIENT_MUTE` role, channel settings, and disables telemetry/GPS on the gateway. It will reboot automatically when done.

---

### Step 3 — Configure Each Sensor Node

1. Connect a sensor node via USB.
2. Review `param_node.py` and update settings if needed (region, channel PSK, intervals).
3. Verify the node's `hop_limit` and `device_role` in `mesh_config.json`.
4. Run the configuration script:

```bash
python node-config.py --node-id 1   # repeat for node IDs 2, 3
```

The node will reboot automatically once all settings are applied.

---

### Step 4 — Verify Node Configuration (Optional)

To confirm a node is online and readable over serial:

```bash
python check-node-info.py
```

---

## Deployment

This section covers the steps required to bring up the full data pipeline: registering nodes, starting the infrastructure containers, and running the gateway receiver. These steps are independent of the hardware configuration steps above and assume the mesh network is already set up.

### Stage 1 — Register a New Node in `mesh_config.json`

Every physical SensCAP node must be registered before it can be configured or have its data routed correctly. When a new node is provided by SensCAP, add it to `mesh_config.json` before running any configuration scripts.

Open `mesh_config.json` and add a new entry under `nodes_cfg`:

```json
{
  "nodes_cfg": {
    "1": {"id": "!0b64122b", "hop_limit": 3, "device_role": "SENSOR"},
    "2": {"id": "!6c73ff1c", "hop_limit": 2, "device_role": "CLIENT"},
    "3": {"id": "!9d84gg2d", "hop_limit": 2, "device_role": "CLIENT"},
    "4": {"id": "!<new_hardware_id>", "hop_limit": 2, "device_role": "CLIENT"}
  }
}
```

**Fields to fill in:**

| Field | Description |
|---|---|
| `id` | Hardware ID printed on the device or readable via `check-node-info.py`. Format: `!xxxxxxxx` |
| `hop_limit` | Number of hops to gateway + 1. Nodes adjacent to the gateway use `2`; farther nodes use `3` |
| `device_role` | `SENSOR` for nodes with active telemetry; `CLIENT` for relay or secondary nodes |

Once registered, follow Steps 1–4 in [Getting Started](#getting-started) to flash, configure, and verify the new node.

---

### Stage 2 — Start the Infrastructure Containers

The data pipeline runs on three Docker services: **Mosquitto** (MQTT broker), **InfluxDB** (time-series database), and **Telegraf** (MQTT → InfluxDB bridge). Start them all with:

```bash
docker compose up -d
```

Verify all three containers are running:

```bash
docker compose ps
```

Expected output:

```
NAME                    IMAGE                    STATUS
telegraf                telegraf:1.32-alpine     Up
influxdb                influxdb:1.11-alpine     Up
brisa-iot-mqtt-broker   eclipse-mosquitto:2.0    Up
```

To inspect logs for any service:

```bash
docker compose logs -f telegraf
docker compose logs -f influxdb
docker compose logs -f mosquitto
```

To stop all containers:

```bash
docker compose down
```

> ℹ️ InfluxDB data is persisted in the `influxdb_data` Docker volume and survives container restarts.

---

### Stage 3 — Run the Gateway Receiver

With the containers running and the LILYGO gateway connected via USB, start the Python receiver:

```bash
source .venv/bin/activate
cd gateway
python receiver.py
```

The receiver listens for telemetry from the mesh network over serial and publishes it to Mosquitto under the `lora-testbed/<node-label>/device` and `lora-testbed/<node-label>/environment` topics. Telegraf picks up these messages and writes them to InfluxDB automatically.

To verify data is flowing, query InfluxDB directly:

```bash
curl -G 'http://localhost:8086/query' \
  --data-urlencode "db=lora_nodes_sensors_db" \
  --data-urlencode "q=SELECT * FROM mqtt_consumer LIMIT 10"
```

---

## Sensors & Data

| Measurement | Status |
|---|---|
| Temperature | ✅ Active |
| Humidity | ✅ Active |
| Power / Battery metrics (`usbPower`, `isCharging`) | 🔧 In progress |
| GPS coordinates | 🔧 Planned |

> ⚠️ USB power and charging state metrics (`usbPower`, `isCharging`) are currently being debugged for correct readings.

---

## Current Status

🔬 **Early / Experimental**

- [x] LoRa mesh network established between 3 nodes and gateway
- [x] Gateway connected to host computer via USB
- [x] Python-based node and gateway configuration via Meshtastic CLI
- [x] Temperature & humidity telemetry
- [x] Per-node hop limit and device role configuration
- [x] Gateway configured as `CLIENT_MUTE` (receive-only)
- [x] MQTT broker, InfluxDB, and Telegraf containerised
- [ ] GPS data collection
- [ ] I2C hub integration for expanded sensing
- [ ] Reliable power/battery metric reporting (`usbPower`, `isCharging`)

---

## Roadmap

### Phase 1 — Application-Layer Configuration *(current)*
Use the Meshtastic CLI and Python to configure nodes and collect environmental telemetry without touching firmware source code.

### Phase 2 — Firmware Customization *(planned)*
Modify Meshtastic firmware source to:
- Add custom sensor integrations (I2C hub, additional peripherals)
- Tune telemetry intervals for solar-optimised low-power operation
- Fix device metric reporting (`usbPower`, `isCharging`)

### Phase 3 — Build From Source *(planned)*
Set up a full PlatformIO environment to compile and flash custom Meshtastic firmware directly onto SensCAP nodes and the LILYGO gateway.

---

## References

- [Meshtastic Documentation](https://meshtastic.org/docs/)
- [Meshtastic Python API](https://python.meshtastic.org/)
- [Meshtastic UF2 Flashing Guide](https://meshtastic.org/docs/getting-started/flashing-firmware/nrf52/drag-n-drop/)
- [Seeed Studio SensCAP Solar Node P1 Pro](https://www.seeedstudio.com/)
- [LILYGO LoRa Boards](https://www.lilygo.cc/)

---

## License

This project is currently unlicensed. License to be determined.

---

*Developed at the Cyber-Physical Systems Research and Technology Center, Pontificia Universidad Católica de Chile.*