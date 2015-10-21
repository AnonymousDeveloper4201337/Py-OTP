from src.connection.ConnectionManager import ConnectionManager
from direct.directnotify import DirectNotifyGlobal
from src.connection.protocol import *
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from src.clientagent.SSLHandler import SSLHandler

class ClientAgent(ConnectionManager, SSLHandler):
    notify = DirectNotifyGlobal.directNotify.newCategory("ClientAgent")
    notify.setInfo(True)

    ourChannel = 100001
    activeConnections = []
    dcFileNames = []
    server_version = "no_version"
    
    def __init__(self, port_address=7101, host_address=7100, ip_address='localhost'):
        ConnectionManager.__init__(self, port_address=port_address, host_address=host_address, ip_address=ip_address)
        SSLHandler.add_certificate(self.socket, ip_address, port_address) # TODO: SSL!
    
    def serverStarted(self, port):
        self.notify.info("Opened connection on port %d" % port)
        if not self.dcFileNames:
        	self.notify.error("No dcFiles specified!")
        self.readDCFile(self.dcFileNames)
    
    def registerChannel(self):
        dg = PyDatagram()
        dg.addUint16(CONTROL_SET_CHANNEL)
        dg.addUint64(self.ourChannel)
        self.cWriter.send(dg, self.connection)
    
    def unregisterChannel(self):
        dg = PyDatagram()
        dg.addUint16(CONTROL_REMOVE_CHANNEL)
        dg.addUint64(self.ourChannel)
        self.cWriter.send(dg, self.connection)
    
    def handleDatagram(self, datagram):
        connection = datagram.getConnection()
        dgi = PyDatagramIterator(datagram)