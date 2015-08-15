import xmlrpclib

#TODO: Get IP address of the user machine directly, no need to pass it to the Create and Delete functions

client_ip1 = "79.79.79.79"
client_ip2 = "192.168.54.14"

str = open ("latency.xml").read()
XMLstring1 = open("topinterferenc1.xml").read()
XMLstring2 = open("topinterferenc2.xml").read()

class wgini_client:
	def __init__(self, ip, port):
		self.conn = xmlrpclib.ServerProxy("http://" + ip + ":" + port)

	def Check(self):
		return self.conn.Check()

	def Create(self, XMLstring, ip):
		return self.conn.Create(XMLstring, ip)

	def Delete(self, ip):
		return self.conn.Delete(ip)

client = wgini_client("192.168.54.14", "8000")


#status = client.Create(XMLstring, client_ip)
status = client.Create(str, client_ip2)
#print status
