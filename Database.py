import sqlite3, os

class WGINI_DB:

	def __init__(self, name):
		# delete database if already exists
		if (os.access(name, os.F_OK)):
			os.remove(name)

		self.conn = sqlite3.connect(name)
		self.c = self.conn.cursor()

		self.conn.execute('pragma foreign_keys=ON')
		self.conn.execute('pragma foreign_keys')

		self.TableCreate()

		# Add Station info into the new database
		self.AddStation("192.168.0.1", 3, 1)
		self.AddStation("192.168.0.2", 3, 0)
		self.AddStation("192.168.0.3", 3, 0)
		self.AddStation("192.168.0.4", 3, 0)
		self.AddStation("192.168.0.5", 3, 0)
		self.AddStation("192.168.0.6", 3, 0)
		self.AddStation("192.168.0.7", 3, 0)
		self.AddStation("192.168.0.8", 3, 0)

	def TableCreate(self):
		self.c.execute("CREATE TABLE Station(ID INTEGER PRIMARY KEY AUTOINCREMENT, IPAddress TEXT, MaxWlanInterfaces INT, IsPortal INT)")
		self.c.execute("CREATE TABLE Topology(ID INTEGER PRIMARY KEY AUTOINCREMENT, HostIP TEXT)")
		self.c.execute('''CREATE TABLE Interface(ID INTEGER PRIMARY KEY AUTOINCREMENT, Type TEXT, InterfaceNo INTEGER, TopologyID INTEGER, StationID INTEGER, DestStaID INTEGER, FOREIGN KEY (TopologyID) REFERENCES Topology(ID), FOREIGN KEY(StationID) REFERENCES Station(ID), FOREIGN KEY(DestStaID) REFERENCES Station(ID))''')

	def AddStation(self, IPAddress, MaxWlanInterfaces, IsPortal):
		self.c.execute("INSERT INTO Station (IPAddress, MaxWlanInterfaces, IsPortal) VALUES (?,?,?)",
			   (IPAddress, MaxWlanInterfaces, IsPortal))
		self.conn.commit()

	def AddTopology(self,HostIP):
		self.c.execute("INSERT INTO Topology (HostIP) VALUES (?)",
			   (HostIP,))
		self.conn.commit()

	def AddInterface(self, Type, InterfaceNo, TopologyID, StationID, DestStaID):
		self.c.execute("INSERT INTO Interface (Type, InterfaceNo, TopologyID, StationID, DestStaID) VALUES (?,?,?,?,?)",
			   (Type, InterfaceNo, TopologyID, StationID, DestStaID))
		self.conn.commit()

	def GetAllStations(self):
		Stations = []
		for AllStationsRow in self.c.execute("SELECT ID FROM Station"):
			Stations.append(AllStationsRow[0])
		return Stations

	# Returns the number of wlan interfaces on each Station (Station, no. of wlan interfaces)
	def GetWlanInfo(self):
		AvailStations = []
		for AllAvailStationsRow in self.c.execute("SELECT Station.ID, COUNT(Interface.ID) FROM Interface LEFT JOIN Station ON Station.ID = Interface.StationID WHERE Interface.Type = 'wlan' GROUP BY Station.ID"):
			AvailStations.append(AllAvailStationsRow)
		return AvailStations

	# Returns topology_id of HostIPToDlt
	def GetTopologyID(self, HostIPToDlt):
		for TopologyIDToDltRow in self.c.execute("SELECT ID FROM Topology WHERE HostIP =?", [(HostIPToDlt)]):
			return 	TopologyIDToDltRow[0]

	# Returns the Stations that have a wlan interface for the topology of HostIPToDlt
	def GetStationsWithWlan(self, HostIPToDlt):
		StationsWithWlan = []
		for StationsWIthWlanRow in self.c.execute("SELECT StationID FROM Interface INNER JOIN Topology ON \
		Interface.TopologyID = Topology.ID WHERE Interface.Type=? AND Topology.HostIP=?", ["wlan", (HostIPToDlt)]):
			StationsWithWlan.append(StationsWIthWlanRow[0])
		return StationsWithWlan

	def GetStationIP(self, StationID):
		for StationIPRow in self.c.execute("SELECT IPAddress FROM Station WHERE ID = %d" %StationID):
			return StationIPRow[0]

	def GetMaxWlan(self, StationID):
		for StationIPRow in self.c.execute("SELECT MaxWlanInterfaces FROM Station WHERE ID = %d" %StationID):
			return StationIPRow[0]

	def GetSpecial(self, StationID):
		for StationIPRow in self.c.execute("SELECT IsPortal FROM Station WHERE ID = %d" %StationID):
			return StationIPRow[0]

	def GetDestInterface(self, StationID, DestStaID, TopID):
		for DestIface in self.c.execute("SELECT InterfaceNo FROM Interface WHERE StationID =? AND DestStaID =? AND TopologyID =? AND Type =?", [(DestStaID), (StationID), (TopID), "tun"]):
			return DestIface[0]

	# Return all Stations used by HostIPToDlt
	def GetStationsUsed(self, HostIPToDlt):
		StationsUsed = []
		for AllStations in self.c.execute("SELECT StationID FROM Interface INNER JOIN Topology ON Interface.TopologyID = Topology.ID \
		WHERE Topology.HostIP=? GROUP BY Interface.StationID", [(HostIPToDlt)]):
			StationsUsed.append(AllStations[0])
		return StationsUsed

	# Deletes all interfaces for HostIPToDlt
	def DeleteInterfaces(self, HostIPToDlt):
		 TopologyToDlt = self.GetTopologyID(HostIPToDlt)
		 self.c.execute("DELETE FROM Interface WHERE TopologyID=%s" %TopologyToDlt)
		 self.conn.commit()

	# Deletes HostIPToDlt's entry from the topology table
	def DeleteTopology(self, HostIPToDlt):
		 self.c.execute("DELETE FROM Topology WHERE HostIP =?", [(HostIPToDlt)])
		 self.conn.commit()
