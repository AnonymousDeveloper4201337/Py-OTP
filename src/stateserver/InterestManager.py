
class InterestHandle:

	def __init__(self, handle, contextId, parentId, zoneId):
		self.handle = handle
		self.contextId = contextId
		self.parentId = parentId
		self.zoneId = zoneId

	def update_interest_location(self, parentId, zoneId):
		self.oldParentId = self.parentId
		self.oldZoneId = self.zoneId

		self.parentId = parentId
		self.zoneId = zoneId

	def update_interest_handle(self, handle, contextId):
		self.oldHandle = self.handle
		self.oldContextId = self.contextId

		self.handle = handle
		self.contextId = contextId

	def post_remove_interest(self, handle, contextId):
		if self.handle == handle:
			if self.contextId == contextId:
				self.remove_interest()

	def remove_interest(self):
		self.oldHandle = self.handle
		self.oldContextId = self.contextId

		self.contextId = None
		self.handle = None