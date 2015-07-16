import xmlrpclib

s = xmlrpclib.ServerProxy('http://127.0.0.1:8000')
XmlString = open("test1.xml").read()
s.Create(XmlString, "192.168.54.14")
