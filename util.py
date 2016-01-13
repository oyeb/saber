import pickle

class Server:
	def __init__(self, pos, power, owner, index):
		self.pos   = pos
		self.power = power
		self.owner = owner

		self._index = 0

	def strify(self):
		return "%f %f %d %d" % (self.pos[0], self.pos[1], self.power, self.owner)
	
	def __repr__(self):
		return ("{O%2d,(%3.3f,%3.3f),p%3d}" % (self.owner, self.pos[0], self.pos[1], self.power))
	
	@property
	# index has no setter
	def index(self):
		return self._index
