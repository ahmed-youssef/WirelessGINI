# WirelessGINI

Wireless GINI is an educational platform for hosting virtual networks. Wireless GINI allows each virtual network to define its own topology and network configuration, while amortizing costs by sharing the physical infrastructure. The platform also creates mechanisms to integrate commodity wireless devices into a deployed virtual network. Wireless GINI provides a user-friendly interface that makes the physical setup process completely transparent to the user. A centralized server is used to provide this transparency, handle user requests, and automatically provision the shared physical infrastructure.

The platform design and implementation was performed as part of my MEng (Thesis) degree. Please refer to [my thesis](https://dl.dropboxusercontent.com/u/14656377/260543987_Youssef_Ahmed_Electrical%20%26%20Computer%20Eng%20%28ECE%29_thesis.pdf) for a more detailed overview of the system.

This repository contains the python code of the WGINI server and client.

![Overview](/Images/WGINIOverview.jpg)

# Installation

No installation or external packages are necessary. The only requirements is python 2.7.3. The system is known to run on Ubuntu 12.04. No other operating systems have been tested.

# Documentation

Documentation for 1) the TSF format using the Document Type Definition (DTD) notation 2) The WGINI APIs that are exposed to the user.

## The Topology Specification File Document Type Definition

Below is the DTD of the TSF. See Example/MyTopology.xml for a TSF example.

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

## The WGINI APIs

- Stations = Server.Check(): Checks available stations and wlan interfaces.
  - Returns the *Stations* object array.
  - *Staion.ID*: The ID of the mesh station.
  - *Station.CurrWlan*: The current number of wlan interfaces deployed on the station.
  - *Station.MaxWlan*: The maximum number of wlan interfaces that this station can support
  - *Station.IsPortal*: A boolean that specifies whether or not this station is the mesh portal.

- Status = Server.Create(UserIP, TSFstring): Deploys the user’s VN as specified by the input TSF.
  - *UserIP*: The IP address of the user who wishes to deploy the VN.
  - *TSFstring*: The TSF file input as a regular string.
  - *Status*: A status code that determines whether or not the operation succeeded.

![CreateAPI](/Images/CreateAPI.jpg)

- Status = Server.Delete(UserIP): Deletes the user’s VN from the wireless mesh platform.
  - *UserIP*: The IP address of the user who wishes to delete his/her VN.
  - *Status*: A status code that determines whether or not the operation succeeded.

![DeleteAPI](/Images/DeleteAPI.jpg)

# Basic Setup

![Image of Physical Setup](/Images/PhysicalSetup.jpg)

Make sure that the wireless mesh network is reachable by the WGINI server. Use the following command on the WGINI server to add a route entry for the mesh:

`route add -net 192.168.0.0 gw yun1.local netmask 255.255.255.0 eth0`

# Usage

We illustrate the usage of the WGINI system through a simple example. In this example:

- The WGINI server's IP address on the LAN is 192.168.55.36
- The WGINI server is listening on TCP port 60000.
- The user machine's IP address on the LAN is 192.168.55.197


## Running the WGINI Server

Run the following script on the WGINI server:

```
From ServerAPI import WGINI_Server

wgini_server = WGINI_Server("192.168.55.36", 60000)
wgini_server.StartServer()

```
That's it! The WGINI server is now listening on TCP port 60000 for incoming requests.


### Running the WGINI Client

Run the following script on the user's machine:

```
From ClientAPI import WGINI_Client

wgini_client = WGINI_Client("192.168.55.36", 60000)
```

This instantiates a WGINI client object that can invoke the WGINI server APIs using RPC. We see how this is done below.

### Invoking the Server APIs

After running the WGINI client on the user machine by instantiating the wgini_client object, we can now invoke the Server APIs.

#### Check API

Run the following code on the user machine to call the Check() function on the WGINI server.

```
# Check the number of stations and the available wlan interfaces
Stations = wgini_client.Check()
for Station in Stations:
  print Station
```

An object array, *Stations* is returned. The object contains the Station's ID, the number of *wlan* interfaces currently deployed on the station, the maximum number of *wlan* interfaces that can be deployed on a station at a given time, and whether or not this station is the mesh portal.

#### Create API

The user creates an XML file "MyTopology.xml" that captures the user's requested topology (see the Example folder for an example of a TSF).

```
# Create Topology using the Topology Specification File
TSF = open("MyTopology.xml").read()
status = wgini_client.Create(TSF, "192.168.55.197")
```
*Status* is a string that indicates whether or not the operation was successful. If the operation is not successful, an explanation is provided.

# Delete Topology

To delete a topology that the user deployed, the user invokes the Delete() function as shown below:

```
status = wgini_client.Delete("192.168.55.197")

```

*Status* is a string that indicates whether or not the operation was successful. If the operation is not successful, an explanation is provided.
