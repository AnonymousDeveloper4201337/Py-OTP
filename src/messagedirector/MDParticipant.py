from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.distributed.PyDatagram import PyDatagram
from src.connection.msgtypes import *
from pandac.PandaModules import *

class MDParticipant:

	def __init__(self):
		pass

	def handleDatagram(self, datagram):
		connection = datagram.getConnection()
		if not connection:
			return

		di = PyDatagramIterator(datagram)
		message_type = di.getUint16()

		if message_type == CONTROL_SET_CHANNEL:
			self.registerChannel(di.getUint64(), connection)
		elif message_type == CONTROL_REMOVE_CHANNEL:
			self.unregisterChannel(di.getUint64())
		elif message_type == CONTROL_MESSAGE:
			self.routeMessage(di.getUint64(), di.getDatagram())

	def registerChannel(self, channel, connection):
		if channel not in self.registeredChannels:
			self.registeredChannels[channel] = connection
		else:
			return

	def unregisterChannel(self, channel):
		if channel in self.registeredChannels:
			del self.registeredChannels[channel]
		else:
			return

	def routeMessage(self, channel, datagram):
		if not datagram:
			return

		di = PyDatagramIterator(datagram)
		# The message director used this value for determining which process the connection requested, but
		# we don't want to send this value over the network because its unnecessary.
		di.skipBytes(16)

		datagram = PyDatagram()
		# Pack the remaining bytes and ship the message out.
		datagram.appendData(di.getRemainingBytes())
		self.routeMessageToChannel(channel, datagram)