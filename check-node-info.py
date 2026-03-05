import meshtastic
import meshtastic.serial_interface

iface = meshtastic.serial_interface.SerialInterface()
node_info = iface.getMyNodeInfo()

print("Node info:")
print(node_info)