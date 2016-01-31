DEFAULT_REGEN = 0.8

MAX_ARATE = 5
CSPEED    = 5
DCSPEED   = 10

class Server:
	def __init__(self, pos, power, maxpow, owner, index):
		self.pos      = pos
		self.reserve  = power
		self.invested = 0
		self.owner    = owner
		# invested + reserve = power
		self._index = index
		self.limit = maxpow
		self.connections = {}

	def strify(self):
		return "%f %f %f %f %f %d" % (self.pos[0], self.pos[1], self.reserve, self.invested, self.limit, self.owner)

	def up_strify(self):
		# used in quantum.get_player_update()
		return "%d %f %f %d" % (self.index, self.reserve, self.invested, self.owner)
	
	def __repr__(self):
		return ("{Own%2d,(%3.3f,%3.3f),res%2.4f,inv%2.4f,lim%2.4f}" % (self.owner, self.pos[0], self.pos[1], self.reserve, self.invested, self.limit))

	def update_pow(self, dr, di):
		if self.reserve < self.limit or dr < 0:
			self.reserve += dr
		else:
			self.reserve = self.limit
		self.invested += di
		return self.reserve
	
	def sync(self, _reserve, _invested, _owner):
		self.reserve = _reserve
		self.invested = _invested
		self.owner = _owner

	def new_connection(self, v_sid, arate, distance, state):
		if v_sid in self.connections.keys():
			raise RuntimeError("Already connected to %d from %d. Something wrong with quantum.py" %(v_sid, self.index))
		else:
			self.connections[v_sid] = Connection(self.index, v_sid, arate, distance, state)

	def update_connection(self, v_sid, arate):
		if v_sid not in self.connections.keys():
			raise RuntimeError("No connection to %d from %d, can't update. First make a connection!" %(v_sid, self.index))

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
		return DEFAULT_REGEN

class Connection:
	STATE_MAP = {'making': 0, 'connected': 1, 'withdrawing': 2, 'headon': 3, 'whostile': 4}
	INV_ST_MAP = {0: 'making', 1: 'connected', 2: 'withdrawing', 3: 'headon', 4: 'whostile'}
	def __init__(self, attacker, victim, arate, distance, state=0):
		self.attacker = attacker
		self.victim = victim
		self._arate = arate
		self.state = state
		self.length = 0
		self.full_distance = distance

	def sync(self, arate, state, length):
		self.arate = arate
		self.state = state
		self.length = length

	def up_strify(self):
		# used in quantum.get_player_update()
		try:
			conv = "%d %d %f %d %f" % (self.attacker, self.victim, self.arate, self.state, self.length)
		except:
			conv = "%d '%s' %f %d %f" % (self.attacker, self.victim, self.arate, self.state, self.length)
		return conv
	
	def __repr__(self):
		if self.state == Connection.STATE_MAP['whostile']:
			return ("{A %d,V %s*,rate %f,%s,%2.4f}" % (self.attacker, self.victim, self.arate, 'whostile', self.length))	
		else:
			return ("{A %d,V %d,rate %f,%s,%2.4f}" % (self.attacker, self.victim, self.arate, Connection.INV_ST_MAP[self.state], self.length))

	@property
	def arate(self):
		return self._arate

	@arate.setter
	def arate(self, val):
		if val < 0 or val > MAX_ARATE:
			raise RuntimeError("Wrong 'new' attack_rate (%f) Acceptable[0, %f]" % (val, MAX_ARATE))
		else:
			self._arate = val