import xmlrpclib

#TODO: Get IP address of the user machine directly, no need to pass it to the Create and Delete functions

class wgini_client:
	def __init__(self, ip, port):
		self.conn = xmlrpclib.ServerProxy("http://" + ip + ":" + port)
		
	def Check(self):
		return self.conn.Check()

	def Create(self, XMLstring, ip):
		return self.conn.Create(XmlString, ip)
		
	def Delete(self, ip):
		return self.conn.Delete(ip)
