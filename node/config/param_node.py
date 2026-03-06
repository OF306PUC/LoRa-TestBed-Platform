# Channel settings 
CHANNEL_IDX = 0
CHANNEL_NAME = "TB CPS-RTC" 
CHANNEL_PSK_B64 = "base64:9z2cyfrgTKeLdD2m0wpvJEUUh1NaHzZ05w1v1LpIEJM="

# LoRa settings: region / preset
LORA_REGION = "ANZ"
LORA_PRESET = "MEDIUM_FAST"
# Rebroadcast mode: only rebroadcast packets from *your* configured channels
REBROADCAST_MODE = "LOCAL_ONLY"

# Telemetry settings
TELEMETRY_DEV_MEAS_ENABLED = True
TELEMETRY_ENV_MEAS_ENABLED = True
TELEMETRY_DEV_UPDATE_INTERVAL = 120     # [seconds]
TELEMETRY_ENV_UPDATE_INTERVAL = 120     # [seconds]

# Sensing node role choice
DEVICE_ROLE_CLIENT = "CLIENT"
DEVICE_ROLE_SENSOR = "SENSOR"

# Hop limit: must be (required_hops_to_gateway + 1)
REQUIRED_HOPS_TO_GATEWAY = 2            # <-- set this per node (e.g., node1=2, node2=1, node3=1)
HOP_LIMIT = REQUIRED_HOPS_TO_GATEWAY + 1

# GPS settings (optional)
GPS_UPDATE_INTERVAL = 300               # [seconds]  