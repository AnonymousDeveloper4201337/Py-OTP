from direct.directnotify import DirectNotifyGlobal
from src.connection.protocol import *
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from src.messagedirector.ChannelWatcher import ChannelWatcher

class MDParticipant(ChannelWatcher):
    notify = DirectNotifyGlobal.directNotify.newCategory("MessageDirectorParticipant")
    notify.setInfo(True)
    
    channelAllocator = None
    canClearChannel = False
    channelWatcher = ChannelWatcher()
    
    def __init__(self, base_class):
        self.base_class = base_class

    def handleDatagram(self, dgi, connection):
        messageType = dgi.getUint16()
        if messageType == CONTROL_SET_CHANNEL:
            self.registerChannel(dgi.getUint64(), connection)
        elif messageType == CONTROL_REMOVE_CHANNEL:
            self.unregisterChannel(dgi.getUint64(), connection)
        elif messageType == CONTROL_MESSAGE:
            self.base_class.routeMessageToChannel(dgi.getUint64(), dgi.getUint64(), dgi.getDatagram(), connection)
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
                self.notify.warning("Participant was not authorized to remove channel: %s" % str(dgi.getUint64()))
                return
        else:
            self.notify.warning("Could not handle incoming datagram: %s" % str(messageType))
            return
    
    def registerChannel(self, channel, connection):
        if channel not in self.base_class.channels:
            if channel is None:
                self.notify.warning("Someone tried to register a channel but the channel value was null!")
                return
            else:
                self.base_class.channels[channel] = connection
                self.channelWatcher.subscribed_channel(channel)
        else:
            self.notify.warning("Channel: %s is already registered!" % str(channel))
            return

    def unregisterChannel(self, channel, connection):
        if channel in self.base_class.channels:
            del self.base_class.channels[channel]
            self.channelWatcher.unsubscribed_channel(channel)
        else:
            self.notify.warning("Channel: %s was never registered!" % str(channel))
            return

    def addChannelRange(self, channelRange):
        pass

    def removeChannelRange(self):
        pass

    def addPostRemove(self, channel):
        pass

    def clearPostRemove(self, channel):
        pass
