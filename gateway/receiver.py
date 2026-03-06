import json
import param as gateway_params  
from mqtt_connector import MQTTConnector
from mesh_receiver import MeshReceiver


def load_known_nodes(config_path: str) -> dict:
    """
    Loads node IDs and labels from mesh_config.json.

    Returns:
        dict: { "!0b64122b": "node-1", ... }
    """
    with open(config_path, "r") as f:
        data = json.load(f)

    known_nodes = {}
    for label, cfg in data["nodes_cfg"].items():
        known_nodes[cfg["id"]] = f"node-{label}"
    return known_nodes


def main():
    known_nodes = load_known_nodes(gateway_params.MESH_CONFIG_PATH)
    print(f"Loaded {len(known_nodes)} known nodes: {known_nodes}\n")

    mqtt = MQTTConnector(
        host=gateway_params.BROKER_ADDRESS, port=gateway_params.BROKER_PORT, client_id=gateway_params.CLIENT_ID
    )
    mqtt.connect()

    receiver = MeshReceiver(mqtt=mqtt, known_nodes=known_nodes)
    receiver.connect()
    receiver.listen()  # blocks until Ctrl+C


if __name__ == "__main__":
    main()