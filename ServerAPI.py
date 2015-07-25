from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from yrouterAPI import *
from XmlAPI import *
from Database import *

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

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

class ServerAPI:

	# Returns an array of all yuns available
	def Check(self):
		YunIDs = database.GetAllYuns()
		YunsWithRaw = database.GetRawInfo()
		Yuns = []
		for YunID in YunIDs:
			Yuns.append(YunEntity(YunID, 0, database.GetMaxRaw(YunID), database.GetSpecial(YunID)))
			# Get the current number of used raw interfaces for the last appended yun
			for AvailYun in YunsWithRaw:
				if(YunID == AvailYun[0]):
					Yuns[-1].CurrRaw = AvailYun[1]
					break

		return Yuns

    # Kills all instances of the topology from the Yuns and updates the database
	def Delete(self, HostIP):
		YunsWithRaw = database.GetYunsWithRaw(HostIP)
		TopID = database.GetTopologyID(HostIP)
		for Yun in YunsWithRaw:
			YunIP = database.GetYunIP(Yun)
			print "Delete: Deleting Raw Interface on Yun%d with IP address %s" %(Yun, YunIP)
			delete_raw_iface(TopID, YunIP)

		YunsUsed = database.GetYunsUsed(HostIP)

		for Yun in YunsUsed:
			YunIP = database.GetYunIP(Yun)
			print "Delete: Killing yRouter on Yun%d with IP address %s" %(Yun, YunIP)
			kill_yrouter(TopID, YunIP)

		database.DeleteInterfaces(HostIP)
		database.DeleteTopology(HostIP)
		return "Delete: Topology %d deleted"%TopID

    # Deploys Topology on Yuns and Updates the database
	def Create(self, XMLstring, HostIP):

		XML = XML_Top(XMLstring)
		XML.Parse()

		# Validation
		Yuns = self.Check()
		for XML_Yun in XML.Yuns:
			# Find Yun object from the Yuns array
			Yun = None
			for CurrYun in Yuns:
				if(XML_Yun.ID == CurrYun.ID):
					Yun = CurrYun
					break

			if( (len(XML_Yun.BBIfaces) > 0) and (Yun.Special != 1)):
				return "Create: Only Mesh Portals can have BBiface"

			RawIfacesLen = len(XML_Yun.RawIfaces)
			if(RawIfacesLen > RawTopMax):
				return "Cannot have more than %d wlan interfaces on a given Yun"%RawTopMax

			if(Yun.CurrRaw + RawIfacesLen > Yun.MaxRaw):
				return "Create: Not enough wlan interfaces on Station %d"%Yun.ID

		database.AddTopology(HostIP)
		TopID = database.GetTopologyID(HostIP)

		for Yun in XML.Yuns:

			for Interface in Yun.BBIfaces:
				database.AddInterface("BB", Interface.num, TopID, Yun.ID, Interface.DestIface)

			for Interface in Yun.TunIfaces:
				database.AddInterface("tun", Interface.num, TopID, Yun.ID, Interface.DestID)

			for Interface in Yun.RawIfaces:
				database.AddInterface("raw", Interface.num, TopID, Yun.ID, None)

		# Run yRouters
		for Yun in XML.Yuns:
			interfaces = ifaces(TopID, database.GetYunIP(Yun.ID))

			for BBiface in Yun.BBIfaces:
				dst_ip = HostIP
				dst_iface = BBiface.DestIface
				interfaces.AddTunIface(tun_iface(BBiface.num, dst_ip, dst_iface, BBiface.vIP, BBiface.vHW, BBiface.routes))

			for tuniface in Yun.TunIfaces:
				dst_ip = database.GetYunIP(tuniface.DestID)
				dst_iface = database.GetDestInterface(Yun.ID, tuniface.DestID, TopID)
				if(dst_iface == None):
					print "Error: Dst Iface not found"
					return "Create: No interface on Station%d for interface on Station%d"%(tuniface.DestID, Yun.ID)

				interfaces.AddTunIface(tun_iface(tuniface.num, dst_ip, dst_iface, tuniface.vIP, tuniface.vHW, tuniface.routes))

			for rawIF in Yun.RawIfaces:
				interfaces.AddRawIface(rawIF)

			run_yrouter(interfaces, Yun.ID)

		return "Create: Topology %d deployed" %TopID

# TODO Put RawTopMax and database into ServerAPI class

# Maximum number of raw interfaces that a topology can deploy on a given Yun
RawTopMax = 1
# Create database instance
database = YunServerDB("YunServer.db")
# Create XMLRPC server
server = SimpleXMLRPCServer(("192.168.54.14", 8000),
                            requestHandler=RequestHandler)
server.register_introspection_functions()
# Register functions
server.register_instance(ServerAPI())
# Run the server's main loop
server.serve_forever()
