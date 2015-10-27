from direct.distributed.PyDatagramIterator import PyDatagramIterator
from src.messagedirector.MDParticipant import MDParticipant
from direct.distributed.PyDatagram import PyDatagram
from direct.task.Task import Task
from pandac.PandaModules import *
from panda3d.core import *

class MessageDirector(MDParticipant):

	registeredChannels = {}

	def __init__(self, tcpPort=7100, threadNet=0):
		self.qcm = QueuedConnectionManager()
		self.qcl = QueuedConnectionListener(self.qcm, threadNet)
		self.qcr = QueuedConnectionReader(self.qcm, threadNet)
		self.cw = ConnectionWriter(self.qcm, threadNet)
		self.start_server(tcpPort)

	def start_server(self, port, backlog=1000):
		self.socket = self.qcm.openTCPServerRendezvous(port, backlog)
		if self.socket:
			self.qcl.addConnection(self.socket)
			taskMgr.add(self.serverListenerPolling, "Poll the connection listener")
			taskMgr.add(self.serverReaderPolling, "Poll the connection reader")

	def serverListenerPolling(self, task):
		if self.qcl.newConnectionAvailable():
			rendezvous = PointerToConnection()
			netAddress = NetAddress()
			newConnection = PointerToConnection()

			if self.qcl.getNewConnection(rendezvous, netAddress, newConnection):
				newConnection = newConnection.p()
				self.qcr.addConnection(newConnection)
  		
		return Task.cont
 
	def serverReaderPolling(self, task):
		if self.qcr.dataAvailable():
			datagram = NetDatagram()
			
			if self.qcr.getData(datagram):
				self.handleDatagram(datagram)

		return Task.cont

	def handleDatagram(self, datagram):
		MDParticipant.handleDatagram(self, datagram)

	def routeMessageToChannel(self, channel, datagram):
		if channel in self.registeredChannels:
			if datagram == None:
				return

			self.cw.send(datagram, self.registeredChannels[channel])
		else:
			return