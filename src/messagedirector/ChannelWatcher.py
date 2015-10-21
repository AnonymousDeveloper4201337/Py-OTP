from direct.directnotify import DirectNotifyGlobal
from src.connection.protocol import *

class ChannelWatcher:

	def __init__(self):
		self.subscribedChannels = 0

	def subscribed_channel(self, channel):
		print(":ChannelWatcher: Subscribed channel %s" % str(channel))
		self.subscribedChannels += channel

	def unsubscribed_channel(self, channel):
		print(":ChannelWatcher: Un-Subscribed channel %s" % str(channel))
		self.subscribedChannels -= channel