import subprocess
import time
import json 
import argparse
import param_node as node_params

MAX_RETRIES = 3
RETRY_DELAY = 10  # seconds to wait before retrying

# Keywords that indicate a transient serial error worth retrying
RETRYABLE_ERRORS = [
    "couldn't be opened",
    "Input/output error",
    "OS Error",
    "serial device",
    "write failed",
]

def is_retryable(stderr: str, stdout: str) -> bool:
    combined = (stderr + stdout).lower()
    return any(keyword.lower() in combined for keyword in RETRYABLE_ERRORS)

def run(cmd, retries=MAX_RETRIES):
    print(f"\nRunning: {cmd}")
    for attempt in range(1, retries + 1):
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.returncode == 0 and not is_retryable(result.stderr, result.stdout):
            time.sleep(2)
            return  # success
        # Something went wrong
        print(f"ERROR (attempt {attempt}/{retries}):", result.stderr or result.stdout)
        if attempt < retries:
            print(f"Retrying in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)
        else:
            print(f"Command failed after {retries} attempts. Continuing...")
            time.sleep(2)

def load_config(node_id): 
    with open("mesh_config.json", "r") as f:
        data = json.load(f)
    
    nodes = data["nodes_cfg"]
    if node_id not in nodes: 
        raise ValueError(f"Node ID {node_id} not found in mesh_config.json")
    return nodes[node_id]

def main():
    parser = argparse.ArgumentParser(description="Configure a LoRa mesh node using meshtastic CLI")
    parser.add_argument("--node-id", type=str, required=True, help="ID of the node to configure (e.g., '1', '2', etc.)")
    
    args = parser.parse_args()
    node_id = args.node_id
    node_cfg = load_config(node_id)
    hop_limit = node_cfg["hop_limit"]
    device_role = node_cfg["device_role"]

    print("Starting node configuration using meshtastic CLI...")

    # LoRa config: region and preset (optional, but recommended to set explicitly)
    run(f"meshtastic --set lora.region {node_params.LORA_REGION}")
    run(f"meshtastic --set lora.modem_preset {node_params.LORA_PRESET}")

    # LoRa hop limit first
    run(f"meshtastic --set lora.hop_limit {hop_limit}")

    # Extra isolation: only rebroadcast packets from *your* configured channels
    run(f"meshtastic --set device.rebroadcast_mode {node_params.REBROADCAST_MODE}")

    # Channel config (this may trigger radio re-init)
    run(
        f'meshtastic --ch-set name "{node_params.CHANNEL_NAME}" '
        f'--ch-set psk {node_params.CHANNEL_PSK_B64} '
        f'--ch-index {node_params.CHANNEL_IDX}'
    )

    # Device role
    run(f"meshtastic --set device.role {device_role}") # it varies by node position.

    # Telemetry config
    DEV_MEAS = str(node_params.TELEMETRY_DEV_MEAS_ENABLED).lower()
    ENV_MEAS = str(node_params.TELEMETRY_ENV_MEAS_ENABLED).lower()
    run(f"meshtastic --set telemetry.device_telemetry_enabled {DEV_MEAS}")
    run(f"meshtastic --set telemetry.environment_measurement_enabled {ENV_MEAS}")
    run(f"meshtastic --set telemetry.device_update_interval {node_params.TELEMETRY_DEV_UPDATE_INTERVAL}")
    run(f"meshtastic --set telemetry.environment_update_interval {node_params.TELEMETRY_ENV_UPDATE_INTERVAL}")

    # GPS config
    run(f"meshtastic --set position.gps_update_interval {node_params.GPS_UPDATE_INTERVAL}")

    # Reboot to apply changes
    run("meshtastic --reboot")


if __name__ == "__main__":
    main()