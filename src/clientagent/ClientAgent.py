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
    dcFileNames = ['dclass/otp.dc', 'dclass/toon.dc']
    server_version = "no_version"

    # Connections
    connection = None
    socket = None
    
    def __init__(self, port_address=7101, host_address=7100, ip_address='localhost'):
        ConnectionManager.__init__(self, port_address=port_address, host_address=host_address, ip_address=ip_address)
        SSLHandler.add_certificate(self.socket, ip_address, port_address) # TODO: SSL!
    
    def serverStarted(self, port):
        self.notify.info("Opened connection on port %d" % port)
        if not self.dcFileNames:
        	self.notify.error("No dcFiles specified!")
        self.readDCFile(self.dcFileNames)
    
    def registerChannel(self, channel):
        dg = PyDatagram()
        dg.addUint16(CONTROL_SET_CHANNEL)
        dg.addUint64(channel)
        self.cWriter.send(dg, self.connection)
    
    def unregisterChannel(self, channel):
        dg = PyDatagram()
        dg.addUint16(CONTROL_REMOVE_CHANNEL)
        dg.addUint64(channel)
        self.cWriter.send(dg, self.connection)
    
    def handleDatagram(self, datagram):
        connection = datagram.getConnection()
        dgi = PyDatagramIterator(datagram)
        message_type = dgi.getUint16()
        print message_type

        if message_type == CLIENT_HEARTBEAT:
        	self.handleClientHeartbeat(dgi, connection)
        elif message_type == CLIENT_DISCONNECT:
        	self.handleClientDisconnect(dgi, connection)

    def handleClientHeartbeat(self, dgi, connection):
    	pass

    def handleClientDisconnect(self, dgi, connection):
    	pass