import xml.etree.ElementTree as etree
from yrouterAPI import raw_iface, rentry

class XML_tuniface:
    def __init__(self, num, DestID, vIP, vHW):
        self.num = num
        self.DestID = DestID
        self.vIP = vIP
        self.vHW = vHW
        self.routes = []

    def AddRoute(self, route):
        self.routes.append(route)

class XML_BBiface:
    def __init__(self, num, DestIface, vIP, vHW):
        self.num = num
        self.DestIface = DestIface
        self.vIP = vIP
        self.vHW = vHW
        self.routes = []

    def AddRoute(self, route):
        self.routes.append(route)

class XML_Yun:
    def __init__(self, ID):
        self.ID = ID
        self.TunIfaces = []
        self.RawIfaces = []
        self.BBIfaces = []

    def AddTunIface(self, TunIface):
        self.TunIfaces.append(TunIface)

    def AddRawIface(self, RawIface):
        self.RawIfaces.append(RawIface)

    def AddBBIface(self, BBIface):
        self.BBIfaces.append(BBIface)

class XML_Top:
    def __init__(self, name):
        self.xmlD = etree.parse(name)
        self.root = self.xmlD.getroot()
        self.Yuns = []

    def Parse(self):
        for Yun in self.root.findall('Yun'):
            ID = int(Yun.find('ID').text)
            nYun = XML_Yun(ID)

            for Interface in Yun.findall('Interface'):
                InterfaceNo = int(Interface.find('InterfaceNo').text)
                DestYunID = int(Interface.find('DestYunID').text)
                IPAddress = Interface.find('IPAddress').text
                HWAddress = Interface.find('HWAddress').text
                TunIface = XML_tuniface(InterfaceNo, DestYunID, IPAddress, HWAddress)
                for REntry in Interface.findall('REntry'):
                    Net = REntry.find('Net').text
                    NetMask = REntry.find('NetMask').text
                    NextHop = REntry.find('NextHop').text
                    route = rentry(Net, NetMask, NextHop)
                    TunIface.AddRoute(route)

                nYun.AddTunIface(TunIface)

            for BBInterface in Yun.findall('BBInterface'):
                InterfaceNo = int(BBInterface.find('InterfaceNo').text)
                DestIface = int(BBInterface.find('DestIface').text)
                IPAddress = BBInterface.find('IPAddress').text
                HWAddress = BBInterface.find('HWAddress').text
                BBIface = XML_BBiface(InterfaceNo, DestIface, IPAddress, HWAddress)
                for REntry in BBInterface.findall('REntry'):
                    Net = REntry.find('Net').text
                    NetMask = REntry.find('NetMask').text
                    NextHop = REntry.find('NextHop').text
                    route = rentry(Net, NetMask, NextHop)
                    BBIface.AddRoute(route)

                nYun.AddBBIface(BBIface)

            for RawInterface in Yun.findall('Raw_Interface'):
                InterfaceNo = int(RawInterface.find('InterfaceNo').text)
                IPAddress = RawInterface.find('IPAddress').text
                RawIface = raw_iface(InterfaceNo, IPAddress)
                for REntry in RawInterface.findall('REntry'):
                    Net = REntry.find('Net').text
                    NetMask = REntry.find('NetMask').text
                    NextHop = REntry.find('NextHop').text
                    route = rentry(Net, NetMask, NextHop)
                    RawIface.AddRoute(route)

                nYun.AddRawIface(RawIface)

            self.AddYun(nYun)

    def AddYun(self, Yun):
        self.Yuns.append(Yun)

    def print_me(self):

        for Yun in self.Yuns:
            print "Yun%d" %Yun.ID
            for TunIface in Yun.TunIfaces:
                print "tun%d Dest=Yun%d vIP=%s vHw=%s" %(TunIface.num, TunIface.DestID, TunIface.vIP, TunIface.vHW)
                for route in TunIface.routes:
                    print "route net=%s netmask=%s gw=%s" %(route.net, route.netmask, route.nexthop)

            for RawIface in Yun.RawIfaces:
                print "raw%d vIP=%s" %(RawIface.num, RawIface.vIP)
                for route in RawIface.routes:
                    print "route net=%s netmask=%s gw=%s" %(route.net, route.netmask, route.nexthop)
