import sqlite3, os, time
from yrouterAPI import *
from XmlAPI import *

class YunEntity:
	def __init__(self, ID, CurrRaw, MaxRaw, Special):
		self.ID = ID
		self.CurrRaw = CurrRaw
		self.MaxRaw = MaxRaw
		self.Special = Special

	def print_me(self):
		print "Yun ID = %d" %self.ID
		print "Current Raw Interfaces = %d" %self.CurrRaw
		print "Max Raw Interfaces = %d" %self.MaxRaw
		print "Special = %d" %self.Special

class YunServerDB:

	def __init__(self, name):
		# delete confFile if already exists
		if (os.access(name, os.F_OK)):
			os.remove(name)

		self.conn = sqlite3.connect(name)
		self.c = self.conn.cursor()

		self.conn.execute('pragma foreign_keys=ON')
		self.conn.execute('pragma foreign_keys')

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

	# Returns an array of all yuns available
	def Check(self):
		YunIDs = self.GetAllYuns()
		YunsWithRaw = self.GetRawInfo()
		Yuns = []
		for YunID in YunIDs:
			Yuns.append(YunEntity(YunID, 0, self.GetMaxRaw(YunID), self.GetSpecial(YunID)))
			# Get the current number of used raw interfaces for the last appended yun
			for AvailYun in YunsWithRaw:
				if(YunID == AvailYun[0]):
					Yuns[-1].CurrRaw = AvailYun[1]
					break

		return Yuns

	def Delete(self, HostIP):
		YunsWithRaw = self.GetYunsWithRaw(HostIP)
		TopID = self.GetTopologyID(HostIP)
		for Yun in YunsWithRaw:
			YunIP = self.GetYunIP(Yun)
			print "Deleting Raw Interface on Yun%d with IP address %s" %(Yun, YunIP)
			delete_raw_iface(TopID, YunIP)

		YunsUsed = self.GetYunsUsed(HostIP)

		for Yun in YunsUsed:
			YunIP = self.GetYunIP(Yun)
			print "Killing yRouter on Yun%d with IP address %s" %(Yun, YunIP)
			kill_yrouter(TopID, YunIP)

		self.DeleteInterfaces(HostIP)
		self.DeleteTopology(HostIP)

	def Create(self, XML_name, HostIP):

		XML = XML_Top(XML_name)
		XML.Parse()

		# Check if we have enough raw interfaces
		Yuns = self.Check()
		for XML_Yun in XML.Yuns:
			for RawIface in XML_Yun.RawIfaces:
				for Yun in Yuns:
					if(XML_Yun.ID == Yun.ID):
						if(Yun.CurrRaw >= Yun.MaxRaw):
							return -1

		self.AddTopology(HostIP)
		TopID = self.GetTopologyID(HostIP)

		for Yun in XML.Yuns:
			for Interface in Yun.TunIfaces:
				self.AddInterface("tun", Interface.num, TopID, Yun.ID, Interface.DestID)

			for Interface in Yun.RawIfaces:
				self.AddInterface("raw", Interface.num, TopID, Yun.ID, None)

		# Run yRouters
		for Yun in XML.Yuns:
			interfaces = ifaces(TopID, self.GetYunIP(Yun.ID))
			for tuniface in Yun.TunIfaces:
				dst_ip = self.GetYunIP(tuniface.DestID)
				dst_iface = self.GetDestInterface(Yun.ID, tuniface.DestID, TopID)

				if(dst_iface == None):
					print "Error: Dst Iface not found"
					return
				interfaces.AddTunIface(tun_iface(tuniface.num, dst_ip, dst_iface, tuniface.vIP, tuniface.vHW, tuniface.routes))

			for BBiface in Yun.BBIfaces:
				dst_ip = HostIP
				dst_iface = BBiface.DestIface
				interfaces.AddTunIface(tun_iface(BBiface.num, dst_ip, dst_iface, BBiface.vIP, BBiface.vHW, BBiface.routes))	

			for rawIF in Yun.RawIfaces:
				interfaces.AddRawIface(rawIF)

			run_yrouter(interfaces, Yun.ID)


yun1_ip = "192.168.0.1"
yun2_ip = "192.168.0.2"
yun3_ip = "192.168.0.3"
yun4_ip = "192.168.0.4"
host1ip = "192.168.54.14"
host2ip = "192.168.54.98"

YunServer = YunServerDB("YunServer.db")
YunServer.TableCreate()

YunServer.AddYun(yun1_ip, 3, 1)
YunServer.AddYun(yun2_ip, 3, 0)
YunServer.AddYun(yun3_ip, 3, 0)
YunServer.AddYun(yun4_ip, 3, 0)

yuns = YunServer.Check()

for yun in yuns:
	yun.print_me()

YunServer.Create("test1.xml", host1ip)
time.sleep(3)
YunServer.Create("test2.xml", host2ip)
