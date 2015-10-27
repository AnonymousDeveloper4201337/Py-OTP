from direct.distributed.PyDatagramIterator import PyDatagramIterator
from src.messagedirector.MDParticipant import MDParticipant
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.MsgTypes import *
from src.connection.msgtypes import *
from direct.task.Task import Task
from pandac.PandaModules import *
from panda3d.core import *
import time

class ClientAgent:

	registeredClients = {}
	connectionToChannel = {v: k for k, v in registeredClients.items()}
	ourChannel = 10000001

	# Heartbeat:
	timeUntilNextHeartbeat = 15
	lastHeartbeatTask = None

	# Channel allocation:
	channelRange = base.config.GetInt('server-channel-range', 4096000)
	channelAllocator = UniqueIdAllocator(0, 0xffffffff / channelRange)

	def __init__(self, tcpPort=6667, server_port=7100, server_ip='localhost', threadNet=0):
		self.qcm = QueuedConnectionManager()
		self.qcl = QueuedConnectionListener(self.qcm, threadNet)
		self.qcr = QueuedConnectionReader(self.qcm, threadNet)
		self.cw = ConnectionWriter(self.qcm, threadNet)
		self.start_connection(server_ip, server_port)
		self.start_server(tcpPort)

	def allocateNewChannel(self):
		return self.channelAllocator.allocate()

	def freeAllocatedChannel(self, channel):
		self.channelAllocator.free(channel)

	def start_server(self, port, backlog=1000):
		self.socket = self.qcm.openTCPServerRendezvous(port, backlog)
		if self.socket:
			self.qcl.addConnection(self.socket)
			taskMgr.add(self.serverListenerPolling, "Poll the connection listener")
			taskMgr.add(self.serverReaderPolling, "Poll the connection reader")

	def start_connection(self, address, port):
		self.connection = self.qcm.openTCPClientConnection(address, port, 3000)
		if self.connection:
			self.qcr.addConnection(self.connection)
			self.registerChannel(self.ourChannel)
			taskMgr.add(self.serverReaderPolling, "Poll the client connection reader")

	def registerChannel(self, channel):
		datagram = PyDatagram()
		datagram.addUint16(CONTROL_SET_CHANNEL)
		datagram.addUint64(channel)
		self.cw.send(datagram, self.connection)
		datagram.clear()

	def unregisterChannel(self, channel):
		datagram = PyDatagram()
		datagram.addUint16(CONTROL_REMOVE_CHANNEL)
		datagram.addUint64(channel)
		self.cw.send(datagram, self.connection)
		datagram.clear()

	def serverListenerPolling(self, task):
		if self.qcl.newConnectionAvailable():
			rendezvous = PointerToConnection()
			netAddress = NetAddress()
			newConnection = PointerToConnection()

			if self.qcl.getNewConnection(rendezvous, netAddress, newConnection):
				newConnection = newConnection.p()
				# TODO: When a client connects allocate them a channel and register their channel to the MessageDirector!
				clientChannel = int(self.allocateNewChannel())
				self.registeredClients[clientChannel] = newConnection
				self.qcr.addConnection(newConnection)
  		
		return Task.cont
 
	def serverReaderPolling(self, task):
		if self.qcr.dataAvailable():
			datagram = NetDatagram()
			
			if self.qcr.getData(datagram):
				self.handleDatagram(datagram)

		return Task.cont

	def handleDatagram(self, datagram):
		connection = datagram.getConnection()

		di = PyDatagramIterator(datagram)
		message_type = di.getUint16()
		print message_type # Debug

		if message_type == CLIENT_HEARTBEAT:
			self.handleClientHeartbeat(di, connection)
		elif message_type == CLIENT_DISCONNECT:
			self.handleClientDisconnected(di, connection)
		elif message_type == CLIENT_ADD_INTEREST:
			self.handleClientAddInterest(di, connection)
		else:
			return

	def sendDisconnectClient(self, di, connection, errorCode, reason):
		datagram = PyDatagram()
		datagram.addUint16(CLIENT_GO_GET_LOST)
		datagram.addUint16(errorCode)
		datagram.addString(reason)
		self.cw.send(datagram, connection)
		datagram.clear()

		self.handleClientDisconnected(di, connection)

	def handleClientHeartbeat(self, di, connection):
		datagram = PyDatagram()
		datagram.addUint16(CLIENT_HEARTBEAT)
		self.cw.send(datagram, connection)

		try:
			if self.lastHeartbeatTask is not None:
				taskMgr.remove(self.lastHeartbeatTask)
		finally:
			self.enterWaitForNextHeartbeat(di, connection, errorCode=1, reason="The server didn't recieve any further heartbeats!")

	def enterWaitForNextHeartbeat(self, di, client, errorCode, reason):
		self.lastHeartbeatTask = taskMgr.doMethodLater(self.timeUntilNextHeartbeat, self.sendDisconnectClient, "noFurtherHeartbeat", extraArgs=[di, client, errorCode, reason])

	def handleClientAddInterest(self, di, connection):
		handle = di.getUint16()
		contextId = di.getUint32()
		parentId = di.getUint32()
		zoneId = di.getUint32()

	def handleClientDisconnected(self, di, connection):
		try:
			channel = self.connectionToChannel[connection]
		except:
			channel = -1

		if channel in self.registeredClients:
			del self.registeredClients[channel]
			self.freeAllocatedChannel(channel)