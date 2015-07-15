from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

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

class ServerAPI:
    def add(self, yun):
        yuns.append(yun)
        print yuns[-1]
        return 1

    def printit(self, index):
        yuns[index].print_me()
        return 1

    def getyuns(self):
        return yuns

yuns = []
yuns.append(YunEntity(1,2,3, 4))
yuns.append(YunEntity(2,5,3, 0))
yuns.append(YunEntity(3,3,3, 0))

# Create XMLRPC server
server = SimpleXMLRPCServer(("127.0.0.1", 8000),
                            requestHandler=RequestHandler)
server.register_introspection_functions()
# Register functions
server.register_instance(ServerAPI())
# Run the server's main loop
server.serve_forever()
