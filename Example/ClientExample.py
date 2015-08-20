From ClientAPI import WGINI_Client

ServerIP = "192.168.55.36"
ServerPort = 60000
ClientIP = "192.168.55.197"

wgini_client = WGINI_Client(ServerIP, ServerPort)

# Check the number of stations and the available wlan interfaces
Stations = wgini_client.Check()
for Station in Stations:
  print Station

# Create Topology using the Topology Specification File
TSF = open("MyTopology.xml").read()
status = wgini_client.Create(TSF, ClientIP)
