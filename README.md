# WirelessGINI

Wireless GINI is an educational platform for hosting virtual networks. Wireless GINI allows each virtual network to define its own topology and network configuration, while amortizing costs by sharing the physical infrastructure. The platform also creates mechanisms to integrate commodity wireless devices into a deployed virtual network. Wireless GINI provides a user-friendly interface that makes the physical setup process completely transparent to the user. A centralized server is used to provide this transparency, handle user requests, and automatically provision the shared physical infrastructure. 

The platform design and implementation was performed as part of my MEng (Thesis) degree. Please refer to [my thesis](https://dl.dropboxusercontent.com/u/14656377/260543987_Youssef_Ahmed_Electrical%20%26%20Computer%20Eng%20%28ECE%29_thesis.pdf) for a more detailed overview of the system.

This repository contains the python code of the WGINI server and client. 

# Installation

No installation or external packages are necessary. The only requirements is python 2.7.3. The system is known to run on Ubuntu 12.04. No other operating systems have been tested.

# Usage

## The WGINI Server

### Running the WGINI Server

```

From ServerAPI import WGINI_Server

# IP address of the interface to listen on
ServerIP = "192.168.55.36"
# TCP port number to listen on
ServerPort = 60000
# Run Server
wgini_server = WGINI_Server(ServerIP, ServerPort)
wgini_server.StartServer()

```

## The WGINI Client

### Running the WGINI Client

```

From ClientAPI import WGINI_Client

wgini_client = WGINI_Client(ServerIP, ServerPort)

```

### Client APIs

```

# Check the number of stations and the available wlan interfaces
Stations = wgini_client.Check()
for Station in Stations:
  print Station
  
# Create Topology using the Topology Specification File 
TSF = open("MyTopology.xml").read()
status = wgini_client.Create(TSF, ClientIP)

# Delete Topology
status = wgini_client.Delete(ClientIP)

```

## The Topology Specification File 

### Document Type Definition

```

<!DOCTYPE VN [
  <!ELEMENT VN (Station+)>
    <!ELEMENT Station (ID, Interface*, BHInterface?, Raw_Interface?)>
      <!ELEMENT ID (#PCDATA)>
      <!ELEMENT Interface (InterfaceNo, DestStaID, IPAddress, HWAddress, REntry+)>
      <!ELEMENT BHInterface (InterfaceNo, DestIface, IPAddress, HWAddress, REntry+)>
      <!ELEMENT WlanInterface (InterfaceNo, IPAddress, SSID, REntry+)>
        <!ELEMENT InterfaceNo (#PCDATA)>
        <!ELEMENT DestStaID (#PCDATA)>
        <!ELEMENT IPAddress (#PCDATA)>
        <!ELEMENT HWAddress (#PCDATA)>
        <!ELEMENT DestIface (#PCDATA)>
        <!ELEMENT REntry (Net, NetMask, NextHop?)>
          <!ELEMENT Net (#PCDATA)>
          <!ELEMENT NetMask (#PCDATA)>
          <!ELEMENT NextHop (#PCDATA)>
]>

```

