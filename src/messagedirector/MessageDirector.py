from src.connection.ConnectionManager import ConnectionManager
from direct.directnotify import DirectNotifyGlobal
from src.connection.protocol import *
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from src.messagedirector.ChannelWatcher import ChannelWatcher
from src.messagedirector.MDParticipant import MDParticipant

class MessageDirector(ConnectionManager, MDParticipant):
    notify = DirectNotifyGlobal.directNotify.newCategory("MessageDirector")
    notify.setInfo(True)

    activeConnections = []
    channels = {}
    interestZones = set()

    def __init__(self, port_address=7100):
        ConnectionManager.__init__(self, port_address=port_address)
        MDParticipant.__init__(self, base_class=self)

    def serverStarted(self, port):
        self.notify.info("Opened connection on port %d" % port)
    
    def handleDatagram(self, datagram):
        MDParticipant.handleDatagram(self, PyDatagramIterator(datagram), connection=datagram.getConnection)

    def routeMessageToChannel(self, channel, sender, datagram, connection): # TODO remove uint16 and add sender!
        if channel in self.channels:
            if self.channels[channel] != connection:
                self.cWriter.send(datagram, self.channel[channel])
            else:
                self.notify.warning("Channel: %s tried to send a datagram to it's self!" % str(channel))
                return
        else:
            self.notify.warning("Channel: %s tried to send a datagram to a un-assigned channel!" % str(channel))
            return

    def addInterest(self, parentId, zoneId):
        self.interestZones.add(zoneId)