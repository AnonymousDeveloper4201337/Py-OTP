from direct.distributed.PyDatagramIterator import PyDatagramIterator
from src.messagedirector.MDParticipant import MDParticipant
from direct.distributed.PyDatagram import PyDatagram
from DistributedObject import DistributedObject
from InterestManager import InterestHandle
from direct.distributed.MsgTypes import *
from src.connection.msgtypes import *
from direct.task.Task import Task
from pandac.PandaModules import *
from panda3d.core import *
import time

class StateServer:

	ourChannel = 10000002

	def __init__(self, server_port=7100, server_ip='localhost', threadNet=0):
		self.qcm = QueuedConnectionManager()
		self.qcl = QueuedConnectionListener(self.qcm, threadNet)
		self.qcr = QueuedConnectionReader(self.qcm, threadNet)
		self.cw = ConnectionWriter(self.qcm, threadNet)
		self.start_connection(server_ip, server_port)

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

		if message_type == CLIENT_AGENT_SET_INTEREST:
			self.handleClientAgentSetInterest(di, sender=di.getUint64(), handle=di.getUint16(), contextId=di.getUint32(), 
											parentId=di.getUint32(), zoneId=di.getUint32())
		elif message_type == CLIENT_AGENT_REMOVE_INTEREST:
			self.handleRemoveInterest(di, sender=di.getUint64(), handle=di.getUint16(), contextId=di.getUint32())

	def handleSetInterest(self, di, channel, sender, handle, contextId, parentId, zoneId):
		if parentId == None:
			return # tried to set interest with an invalid parentId

		self.interest = InterestHandle(handle, contextId, parentId, zoneId)

		if self.interest.handle != handle or self.interest.contextId != contextId: # This should never happen, but if for some reason...
			self.interest.update_interest_handle(handle, contextId)

		if self.interest.parentId != parentId or self.interest.zoneId != zoneId: # ^
			self.interest.update_interest_location(parentId, zoneId)

		self.sendAddInterest(di, sender, handle, contextId, parentId, zoneId)

	def sendAddInterest(self, di, sender, handle, contextId, parentId, zoneId):
		datagram = PyDatagram()
		datagram.addUint16(CONTROL_MESSAGE)
		datagram.addUint64(sender)
		datagram.addUint64(self.ourChannel)
		datagram.addUint16(STATESERVER_BOUNCE_MESSAGE)
		datagram.addUint16(CLIENT_AGENT_SET_INTEREST)
		datagram.addUint16(handle)
		datagram.addUint32(contextId)
		datagram.addUint32(parentId) # Not really needed, but maybe i can find a use for this later...
		datagram.addUint32(zoneId) # ^
		self.cw.send(datagram, self.connection)

	def handleRemoveInterest(self, di, sender, handle, contextId):
		if not self.interest:
			return # tried to remove interest that was never set!

		self.interest.post_remove_interest(handle, contextId)
		self.sendRemoveInterest(sender, handle, contextId)

	def sendRemoveInterest(self, handle, contextId):
		datagram = PyDatagram()
		datagram.addUint16(CONTROL_MESSAGE)
		datagram.addUint64(sender)
		datagram.addUint64(self.ourChannel)
		datagram.addUint16(STATESERVER_BOUNCE_MESSAGE)
		datagram.addUint16(CLIENT_AGENT_REMOVE_INTEREST)
		datagram.addUint16(handle)
		datagram.addUint32(contextId)
		self.cw.send(datagram, self.connection)