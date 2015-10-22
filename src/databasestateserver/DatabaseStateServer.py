from src.connection.ConnectionManager import ConnectionManager
from direct.directnotify import DirectNotifyGlobal
from src.connection.protocol import *
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

class DatabaseStateServer(ConnectionManager):
    notify = DirectNotifyGlobal.directNotify.newCategory("DatabaseStateServer")
    notify.setInfo(True)

    ourChannel = 100004
    activeConnections = []

    # Connections
    connection = None
    socket = None
    
    def __init__(self, host_address=7100, ip_address='localhost'):
        ConnectionManager.__init__(self, host_address=host_address, ip_address=ip_address)
    
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