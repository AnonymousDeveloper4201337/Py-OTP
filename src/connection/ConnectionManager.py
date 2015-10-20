from direct.directnotify import DirectNotifyGlobal
from direct.task.TaskManagerGlobal import *
from direct.task.Task import Task
from pandac.PandaModules import *
from panda3d.core import *

class ConnectionManager(QueuedConnectionManager):
    notify = DirectNotifyGlobal.directNotify.newCategory("ConnectionManager")

    def __init__(self, port_address, backlog=10000):
        self.cManager = QueuedConnectionManager()
        self.cListener = QueuedConnectionListener(self.cManager, 0)
        self.cReader = QueuedConnectionReader(self.cManager, 0)
        self.cWriter = ConnectionWriter(self.cManager, 0)
        self.activeConnections = []
        self.port_address = port_address
        self.backlog = backlog

        if self.port_address:
            self.setup()
    
    def setup(self):
        self.socket = self.cManager.openTCPServerRendezvous(self.port_address, self.backlog)
        if self.socket:
            self.cListener.addConnection(self.socket)
            taskMgr.add(self.socketListener, 'Poll the connection listener')
            taskMgr.add(self.socketReader, 'Poll the connection reader')
    
    def socketListener(self, task):
        if self.cListener.newConnectionAvailable():
            rendezvous = PointerToConnection()
            netAddress = NetAddress()
            newConnection = PointerToConnection()

            if self.cListener.getNewConnection(rendezvous, netAddress, newConnection):
                newConnection = newConnection.p()
                self.activeConnections.append(newConnection)
                self.cReader.addConnection(newConnection)

        return Task.cont
    
    def socketReader(self, task):
        if self.cReader.dataAvailable():
            datagram = NetDatagram()

            if self.cReader.getData(datagram):
                self.handleDatagram(datagram)

        return Task.cont
    
    def handleDatagram(self, datagram):
        connection = datagram.getConnection()
        dgi = PyDatagramIterator(datagram)
        messageType = dgi.getUint16()