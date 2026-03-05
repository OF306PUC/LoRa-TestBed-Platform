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

### Mesh Network Topology

![Mesh Network Graph](docs/sensecap-mesh-mesh.drawio.png)

---

## Repository Structure

```
LoRa-TestBed-Platform/
│
├── UF2/                          # UF2 firmware binaries for flashing devices
├── docs/                         # Documentation and reference material
│   ├── senscap-node.png          # SensCAP node architecture diagram
│   └── senscap-mesh.png          # Mesh network topology graph
│
├── node-config.py                # Main script: configures nodes via Meshtastic CLI
├── params.py                     # Shared configuration parameters and constants
│
├── config.yaml                   # General device/mesh configuration
├── firmware_inital_config.yaml   # Initial firmware configuration for new nodes
├── mesh_config.json              # Per-node mesh parameters (roles, hop limits, etc.)
│
└── README.md
```

---

## File Descriptions

### `params.py` — Shared Parameters

Centralises all configurable constants used by the configuration scripts:

- **Channel settings** — channel index, name (`TB CPS-RTC`), and PSK key (base64-encoded)
- **LoRa radio settings** — region (`ANZ`) and modem preset (`MEDIUM_FAST`)
- **Rebroadcast mode** — set to `LOCAL_ONLY` to isolate the mesh from foreign traffic
- **Telemetry intervals** — environment measurements sent every `120` seconds; device metrics on demand
- **Device roles** — `CLIENT` (gateway) or `SENSOR` (field nodes)
- **Hop limit** — computed as `REQUIRED_HOPS_TO_GATEWAY + 1`; must be set per node
- **GPS settings** — optional GPS reporting every `300` seconds

### `node-config.py` — Node Configuration Script

Main script that configures a single node via the Meshtastic CLI. Run it once per node, passing the target node ID as an argument. It applies the following in order:

1. Sets LoRa region and modem preset
2. Sets the hop limit (loaded from `mesh_config.json` per node)
3. Sets rebroadcast mode to `LOCAL_ONLY`
4. Configures the private mesh channel (name + PSK)
5. Sets the device role (`CLIENT` or `SENSOR`)
6. Enables environment telemetry and sets update intervals
7. Reboots the node to apply all changes

**Usage:**
```bash
python node-config.py --node-id <ID>
```

For example, to configure node 1:
```bash
python node-config.py --node-id 1
```

### `mesh_config.json` — Per-Node Mesh Parameters

Defines per-node settings such as `device_role` and `hop_limit` for each node ID. Referenced at runtime by `node-config.py`.

### `firmware_inital_config.yaml` / `config.yaml`

YAML configuration files for initial device setup and general runtime settings respectively. Used as reference when provisioning new nodes.

---

## Flashing Meshtastic Firmware

The `UF2/` folder contains firmware binaries for supported devices. To flash a device using drag-and-drop (no tools required):

👉 [Meshtastic UF2 Drag-and-Drop Flashing Guide](https://meshtastic.org/docs/getting-started/flashing-firmware/nrf52/drag-n-drop/)

---

## Getting Started

### Prerequisites

- Python 3.8+
- LILYGO gateway connected via USB
- Meshtastic firmware flashed on all nodes and the gateway (see flashing guide above)
- Meshtastic Python CLI

### Installation

```bash
# Clone the repository
git clone https://github.com/OF306PUC/LoRa-TestBed-Platform.git
cd LoRa-TestBed-Platform

# Install the Meshtastic CLI
pip install meshtastic
```

### Configuring a Node

1. Connect the target node via USB.
2. Review `params.py` and update any settings as needed (e.g. region, channel PSK, intervals).
3. Set the correct `hop_limit` and `device_role` for each node in `mesh_config.json`.
4. Run the configuration script:

```bash
python node-config.py --node-id 1   # repeat for node IDs 2, 3, etc.
```

The node will automatically reboot once all settings are applied.

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
- [x] Python-based node configuration via Meshtastic CLI
- [x] Temperature & humidity telemetry
- [x] Per-node hop limit and device role configuration
- [ ] GPS data collection
- [ ] I2C hub integration for expanded sensing
- [ ] Reliable power/battery metric reporting (`usbPower`, `isCharging`)
- [ ] Data logging pipeline

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
