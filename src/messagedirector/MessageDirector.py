from src.connection.ConnectionManager import ConnectionManager
from src.connection.protocol import *

class MDParticipantInterface:
    
    channelAllocator = None
    canClearChannel = False
    
    def __init__(self, base_class):
        self.base_class = base_class

    def handleDatagram(self):
        if messageType == CONTROL_SET_CHANNEL:
            self.registerChannel(dgi.getUint64(), connection)
        elif messageType == CONTROL_REMOVE_CHANNEL:
            self.unregisterChannel(dgi.getUint64(), connection)
        elif messageType == CONTROL_MESSAGE:
            self.base_class.routeMessageToChannel(dgi.getUint64(), dgi.getDatagram(), connection)
        elif messageType == CONTROL_ADD_RANGE:
            self.addChannelRange(dgi.getUint64())
        elif messageType == CONTROL_REMOVE_RANGE:
            self.removeChannelRange()
        elif messageType == CONTROL_ADD_POST_REMOVE:
            self.addPostRemove(dgi.getUint64())
        elif messageType == CONTROL_CLEAR_POST_REMOVE:
            if canClearChannel:
                self.clearPostRemove(dgi.getUint64())
            else:
                return # participant was not authorized to remove channel.
        else:
            return # Could not handle the incoming datagram!
    
    def registerChannel(self, channel, connection):
        if channel not in self.base_class.channels:
            if channel is None:
                return # No channel was specified.
            else:
				self.base_class.channels[channel] = connection
        else:
            return # Channel: is already assigned!

    def unregisterChannel(self, channel, connection):
        if channel in self.base_class.channels:
            if self.base_class.channels[channel] == connection:
                del self.base_class[channel]
            else:
				return # Channel: was assigned to the wrong connection!
        else:
            return # Channel: was never registered!

    def addChannelRange(self, channelRange):
        pass

    def removeChannelRange(self):
        pass

    def addPostRemove(self, channel):
        pass

    def clearPostRemove(self, channel):
        pass

class MessageDirector(ConnectionManager, MDParticipantInterface):

    channels = {}
    interestZones = set()

    def __init__(self, port_address=7100):
        ConnectionManager.__init__(port_address=port_address)
        MDParticipantInterface.__init__(self, base_class=self)
    
    def handleDatagram(self, datagram):
        ConnectionManager.handleDatagram(self, datagram)
        MDParticipantInterface.handleDatagram(self, datagram)

    def routeMessageToChannel(self, channel, datagram, connection):
        if channel in self.channels:
            if self.channels[channel] != connection:
                self.cWriter.send(datagram, self.channel[channel])
            else:
                return # Channel: Tried to send a datagram to its self.
        else:
            return # Channel: Tried to send a datagram to un-assigned channel!

    def addInterest(self, parentId, zoneId): # TODO!
        self.interestZones.add(zoneId)