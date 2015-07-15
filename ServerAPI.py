from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
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
			print "Deleting Raw Interface on Yun%d with IP address %s" %(Yun, YunIP)
			delete_raw_iface(TopID, YunIP)

		YunsUsed = database.GetYunsUsed(HostIP)

		for Yun in YunsUsed:
			YunIP = database.GetYunIP(Yun)
			print "Killing yRouter on Yun%d with IP address %s" %(Yun, YunIP)
			kill_yrouter(TopID, YunIP)

		database.DeleteInterfaces(HostIP)
		database.DeleteTopology(HostIP)
		return 1

    # Deploys Topology on Yuns and Updates the database
	def Create(self, XMLstring, HostIP):

		XML = XML_Top(XMLstring)
		XML.Parse()

		# Check if we have enough raw interfaces
		Yuns = database.Check()
		for XML_Yun in XML.Yuns:
			for RawIface in XML_Yun.RawIfaces:
				for Yun in Yuns:
					if(XML_Yun.ID == Yun.ID):
						if(Yun.CurrRaw >= Yun.MaxRaw):
							return -1

		database.AddTopology(HostIP)
		TopID = database.GetTopologyID(HostIP)

		for Yun in XML.Yuns:
			for Interface in Yun.TunIfaces:
				database.AddInterface("tun", Interface.num, TopID, Yun.ID, Interface.DestID)

			for Interface in Yun.RawIfaces:
				database.AddInterface("raw", Interface.num, TopID, Yun.ID, None)

		# Run yRouters
		for Yun in XML.Yuns:
			interfaces = ifaces(TopID, database.GetYunIP(Yun.ID))
			for tuniface in Yun.TunIfaces:
				dst_ip = database.GetYunIP(tuniface.DestID)
				dst_iface = database.GetDestInterface(Yun.ID, tuniface.DestID, TopID)

				if(dst_iface == None):
					print "Error: Dst Iface not found"
					return -1
				interfaces.AddTunIface(tun_iface(tuniface.num, dst_ip, dst_iface, tuniface.vIP, tuniface.vHW, tuniface.routes))

			for BBiface in Yun.BBIfaces:
				dst_ip = HostIP
				dst_iface = BBiface.DestIface
				interfaces.AddTunIface(tun_iface(BBiface.num, dst_ip, dst_iface, BBiface.vIP, BBiface.vHW, BBiface.routes))

			for rawIF in Yun.RawIfaces:
				interfaces.AddRawIface(rawIF)

			run_yrouter(interfaces, Yun.ID)

		return 1

# Create database instance
database = YunServerDB("YunServer.db")
# Create XMLRPC server
server = SimpleXMLRPCServer(("127.0.0.1", 8000),
                            requestHandler=RequestHandler)
server.register_introspection_functions()
# Register functions
server.register_instance(ServerAPI())
# Run the server's main loop
server.serve_forever()
