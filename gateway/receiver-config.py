import subprocess
import time
import param_receiver as node_params

def run(cmd):
    print(f"\nRunning: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print("ERROR:", result.stderr)
    time.sleep(5)  

def main():
    print("Starting node configuration using meshtastic CLI...")

    # LoRa config: region and preset (optional, but recommended to set explicitly)
    run(f"meshtastic --set lora.region {node_params.LORA_REGION}")
    run(f"meshtastic --set lora.modem_preset {node_params.LORA_PRESET}")

    # Channel config (this may trigger radio re-init)
    run(
        f'meshtastic --ch-set name "{node_params.CHANNEL_NAME}" '
        f'--ch-set psk {node_params.CHANNEL_PSK_B64} '
        f'--ch-index {node_params.CHANNEL_IDX}'
    )

    # Device role
    run(f"meshtastic --set device.role {node_params.DEVICE_ROLE}") 
    
    # Telemetry config
    DEV_MEAS = str(node_params.TELEMETRY_DEV_MEAS_ENABLED).lower()
    ENV_MEAS = str(node_params.TELEMETRY_ENV_MEAS_ENABLED).lower()
    run(f"meshtastic --set telemetry.device_telemetry_enabled {DEV_MEAS}")
    run(f"meshtastic --set telemetry.environment_measurement_enabled {ENV_MEAS}")

    # GPS config
    run(f"meshtastic --set position.gps_mode {node_params.POSITION_GPS_MODE_ENABLED}")

    # Reboot to apply changes
    run("meshtastic --reboot")


if __name__ == "__main__":
    main()
