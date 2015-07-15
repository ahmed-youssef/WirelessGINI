import xmlrpclib


s = xmlrpclib.ServerProxy('http://127.0.0.1:8000')
print s.printit(0)
