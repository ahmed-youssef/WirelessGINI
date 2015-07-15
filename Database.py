import sqlite3, os

class YunServerDB:

	def __init__(self, name):
		# delete database if already exists
		if (os.access(name, os.F_OK)):
			os.remove(name)

		self.conn = sqlite3.connect(name)
		self.c = self.conn.cursor()

		self.conn.execute('pragma foreign_keys=ON')
		self.conn.execute('pragma foreign_keys')

		self.TableCreate()

		# Add Yun info into the new database
		self.AddYun("192.168.0.1", 3, 1)
		self.AddYun("192.168.0.2", 3, 0)
		self.AddYun("192.168.0.3", 3, 0)
		self.AddYun("192.168.0.4", 3, 0)

	def TableCreate(self):
		self.c.execute("CREATE TABLE Yun(ID INTEGER PRIMARY KEY AUTOINCREMENT, IPAddress TEXT, MaxRawInterfaces INT, Special INT)")
		self.c.execute("CREATE TABLE Topology(ID INTEGER PRIMARY KEY AUTOINCREMENT, HostIP TEXT)")
		self.c.execute('''CREATE TABLE Interface(ID INTEGER PRIMARY KEY AUTOINCREMENT, Type TEXT, InterfaceNo INTEGER, TopologyID INTEGER, YunID INTEGER, YunDestID INTEGER, FOREIGN KEY (TopologyID) REFERENCES Topology(ID), FOREIGN KEY(YunID) REFERENCES Yun(ID), FOREIGN KEY(YunDestID) REFERENCES Yun(ID))''')

	def AddYun(self, IPAddress, MaxRawInterfaces, Special):
		self.c.execute("INSERT INTO Yun (IPAddress, MaxRawInterfaces, Special) VALUES (?,?,?)",
			   (IPAddress, MaxRawInterfaces, Special))
		self.conn.commit()

	def AddTopology(self,HostIP):
		self.c.execute("INSERT INTO Topology (HostIP) VALUES (?)",
			   (HostIP,))
		self.conn.commit()

	def AddInterface(self, Type, InterfaceNo, TopologyID, YunID, YunDestID):
		self.c.execute("INSERT INTO Interface (Type, InterfaceNo, TopologyID, YunID, YunDestID) VALUES (?,?,?,?,?)",
			   (Type, InterfaceNo, TopologyID, YunID, YunDestID))
		self.conn.commit()

	def GetAllYuns(self):
		Yuns = []
		for AllYunsRow in self.c.execute("SELECT ID FROM Yun"):
			Yuns.append(AllYunsRow[0])
		return Yuns

	# Returns the number of raw interfaces on each yun (yun, no. of raw interfaces)
	def GetRawInfo(self):
		AvailYuns = []
		for AllAvailYunsRow in self.c.execute("SELECT Yun.ID, COUNT(Interface.ID) FROM Interface LEFT JOIN Yun ON Yun.ID = Interface.YunID WHERE Interface.Type = 'raw' GROUP BY Yun.ID"):
			AvailYuns.append(AllAvailYunsRow)
		return AvailYuns

	# Returns topology_id of HostIPToDlt
	def GetTopologyID(self, HostIPToDlt):
		for TopologyIDToDltRow in self.c.execute("SELECT ID FROM Topology WHERE HostIP =?", [(HostIPToDlt)]):
			return 	TopologyIDToDltRow[0]

	# Returns the Yuns that have a raw interface for the topology of HostIPToDlt
	def GetYunsWithRaw(self, HostIPToDlt):
		YunsWithRaw = []
		for YunsWIthRawRow in self.c.execute("SELECT YunID FROM Interface INNER JOIN Topology ON \
		Interface.TopologyID = Topology.ID WHERE Interface.Type=? AND Topology.HostIP=?", ["raw", (HostIPToDlt)]):
			YunsWithRaw.append(YunsWIthRawRow[0])
		return YunsWithRaw

	def GetYunIP(self, YunID):
		for YunIPRow in self.c.execute("SELECT IPAddress FROM Yun WHERE ID = %d" %YunID):
			return YunIPRow[0]

	def GetMaxRaw(self, YunID):
		for YunIPRow in self.c.execute("SELECT MaxRawInterfaces FROM Yun WHERE ID = %d" %YunID):
			return YunIPRow[0]

	def GetSpecial(self, YunID):
		for YunIPRow in self.c.execute("SELECT Special FROM Yun WHERE ID = %d" %YunID):
			return YunIPRow[0]

	def GetDestInterface(self, YunID, DestYunID, TopID):
		for DestIface in self.c.execute("SELECT InterfaceNo FROM Interface WHERE YunID =? AND YunDestID =? AND TopologyID =? AND Type =?", [(DestYunID), (YunID), (TopID), "tun"]):
			return DestIface[0]

	# Return all yuns used by HostIPToDlt
	def GetYunsUsed(self, HostIPToDlt):
		YunsUsed = []
		for AllYuns in self.c.execute("SELECT YunID FROM Interface INNER JOIN Topology ON Interface.TopologyID = Topology.ID \
		WHERE Topology.HostIP=? GROUP BY Interface.YunID", [(HostIPToDlt)]):
			YunsUsed.append(AllYuns[0])
		return YunsUsed

	# Deletes all interfaces for HostIPToDlt
	def DeleteInterfaces(self, HostIPToDlt):
		 TopologyToDlt = self.GetTopologyID(HostIPToDlt)
		 self.c.execute("DELETE FROM Interface WHERE TopologyID=%s" %TopologyToDlt)
		 self.conn.commit()

	# Deletes HostIPToDlt's entry from the topology table
	def DeleteTopology(self, HostIPToDlt):
		 self.c.execute("DELETE FROM Topology WHERE HostIP =?", [(HostIPToDlt)])
		 self.conn.commit()
