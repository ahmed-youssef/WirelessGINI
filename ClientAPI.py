import xmlrpclib

XmlString = open("test1.xml").read()

yuns = YunServer.Check()

for yun in yuns:
	print yun

s = xmlrpclib.ServerProxy('http://127.0.0.1:8000')

s.Create(XmlString, "192.168.54.14")
