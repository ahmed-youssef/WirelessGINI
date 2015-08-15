import xmlrpclib

class WGINI_Client:
	def __init__(self, ip, port):
		self.conn = xmlrpclib.ServerProxy("http://" + ip + ":" + str(port))

	def Check(self):
		return self.conn.Check()

	def Create(self, XMLstring, ip):
		return self.conn.Create(XMLstring, ip)

	def Delete(self, ip):
		return self.conn.Delete(ip)
