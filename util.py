class Server:
	def __init__(self, pos, power, owner, maxpow, index):
		self.pos      = pos
		self.reserve  = power
		self.invested = 0
		self.owner    = owner
		# invested + reserve = power
		self._index = index
		self.limit = maxpow

	def strify(self):
		return "%f %f %f %f %d" % (self.pos[0], self.pos[1], self.reserve, self.invested, self.owner)
	
	def __repr__(self):
		return ("{Own%2d,(%3.3f,%3.3f),res%f,inv%f}" % (self.owner, self.pos[0], self.pos[1], self.reserve, self.invested))

	def update_pow(self, dr, di):
		self.reserve += dr
		self.invested += di
		return self.reserve
	
	@property
	# index has no setter
	def index(self):
		return self._index

	@property
	# power has no setter
	def power(self):
		return self.reserve + self.invested

	@property
	# regen_rate has no setter
	def regen_rate(self):
		return 0.8