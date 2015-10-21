from direct.directnotify import DirectNotifyGlobal
from src.connection.protocol import *

class ChannelWatcher:
	notify = DirectNotifyGlobal.directNotify.newCategory("ChannelWatcher")
	notify.setInfo(True)

	def __init__(self):
		self.subscribedChannels = 0

	def subscribed_channel(self, channel):
		self.notify.info("Subscribed channel %s" % str(channel))
		self.subscribedChannels += channel

	def unsubscribed_channel(self, channel):
		self.notify.info("Un-Subscribed channel %s" % str(channel))
		self.subscribedChannels -= channel