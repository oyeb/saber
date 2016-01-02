import random

sample_map = ['port', 'sost', 'kail', 'mugs']
VALID_ORDERS = {'s':('swap', 4),
				'e':('edit', 3)}
class Game:
	def __init__(self, options):
		self.mapfile = options["map"]
		self.turntime = options["turntime"]
		self.loadtime = options["loadtime"]
		self.bot_count = options["bot_count"]
		self.mapdata, self.size = self.parse_map(options["map"])

		self.turn = 0
		self.scores = [0] * self.bot_count
		self.active = [True] * self.bot_count
		self.killed = [False] * self.bot_count # if True, it denotes that a bot malfunctioned and was killed by the system

	def parse_map(self, mf):
		words = []
		with iter(open(mf, 'r')) as map_file_iter:
			for map_line in map_file_iter:
				words.append(map_line.strip('\r\n'))
		return words, len(words)

	def start_game(self):
		pass

	def get_start_player(self, player=None):
		# common start data, for the game_log here
		res = ["turn 0"]
		res.append("turntime %d" % self.turntime)
		res.append("loadtime %d" % self.loadtime)
		res.append("bots %d" % (self.bot_count-1)) # number of other bots
		# player specific data here
		if player != None:
			pass
		# map here
		for w in self.mapdata:
			res.append("m %s" % w)
		return '\n'.join(res)

	def start_turn(self):
		self.turn += 1
		self.orders = [[] for i in range(self.bot_count)] # this is filled by do_moves

	def get_current_state():
		"""
		Used only for logging the game-level log
		"""
		res = ""
		for i in range(self.bot_count):
			res += "bot %2d : %s" % (i, str(self.is_alive(i)))
		map_lines = '\n'.join(self.mapdata) + '\n'
		score_line = ' '.join(self.scores) + '\n'
		return '___\n'

	def parse_move(self, move):
		"""
		validate moves, only check if formatting  and data-type is correct
		"""
		orders  = []
		valid   = []
		invalid = []
		for l in move:
			line = l.strip('\r\n').lower()
			# ignore blank lines or comments (Just in case some dumbass wants to debug via the stdout)
			if not line or line[0] == '#':
				continue
			data = line.split(' ')
			if data[0] == 's':
				# swap
				if len(data[1:]) != VALID_ORDERS['s'][1]:
					invalid.append("%s {invalid formatting!}" % line)
					continue
				else:
					r1, c1, r2, c2 = data[1:]
					# validate data-types
					try:
						loc1 = int(r1), int(c1)
						loc2 = int(r2), int(c2)
						orders.append( ('s', (loc1, loc2)) )
						valid.append(line)
					except:
						invalid.append("%s {Invalid `row` or `col`}" % line)
			elif data[0] == 'e':
				# edit
				if len(data[1:]) != VALID_ORDERS['e'][1]:
					invalid.append("%s {invalid formatting!}" % line)
					continue
				else:
					r, c, ch = data[1:]
					# validate data-types
					try:
						loc = int(r), int(c)
					except:
						invalid.append("%s {Invalid `row` or `col`}" % line)
					try:
						if ord(ch) > 96 and ord(ch) < 123:
							orders.append( ('e', (loc, ch)) )
							valid.append(line)
						else:
							raise
					except:
						invalid.append("%s {Invalid replacement character}" % line)
			else:
				invalid.append("%s {Unknown Action!} [%s]" %(data[0], line))
		
		"""
		Now, we must validate these moves, by calling self.validate_moves()
		"""
		return self.validate_moves(orders, valid, invalid)

	def validate_move(self, orders, valid, invalid):
		"""
		Valid move might turn into invalid or ignored ones.
		Check for out of bound map access and other illegal things here:

		* Out-Of-Bounds
		"""
		seen_locations = set() # can't daisy chain locations
		valid_orders   = []
		valid_lines    = []
		ignored        = []		
		for line, order in zip(valid, orders):
			if order[0] == 's':
				if self.out_of_bounds(order[1][0]) or self.out_of_bounds(order[1][1]):
					invalid.append("%s {Out of Bounds!}" % line)
					continue
				elif order[1][0] in seen_locations or order[1][1] in seen_locations:
					invalid.append("%s {Duplicate location, possible daisy chaining!}" % line)
					continue
				else:
					seen_locations.add(order[1][1])
			if order[0] == 'e':
				if self.out_of_bounds(order[1][0]):
					invalid.append("%s {Out of Bounds!}" % line)
					continue
				elif order[1][0] in seen_locations:
					invalid.append("%s {Duplicate location, possible daisy chaining!}" % line)
					continue
			valid_orders.append(order)
			valid_lines.append(line)
			seen_locations.add(order[1][0])

		return valid_orders, valid_lines, invalid, ignored

	def do_move(self, player_id, moves):
		# parse and validate moves
		orders, valid_lines, invalid_lines, ignored = self.parse_move(moves)
		# store this guy's orders here. This is reset @ self.start_turn()
		self.orders[player_id] = orders
		return valid_lines, invalid_lines, ignored

	def finish_turn(self):
		for pid, _orders in enumerate(self.orders):
			if _orders:
				for mode, args in _orders:
					if mode == 'e':
						r, c = args[0]
						self.words[r][c] = args[1]
					if mode == 's':
						r1, c1 = args[0]
						r2, c2 = args[1]
						self.words[r1][c1], self.words[r2][c2] = self.words[r2][c2], self.words[r1][c1]
					# Award scores, or some helper computes for "this player"
			self.scores[pid] += 1
		# update vision
		# update ranks or cutoff level of the game?

	def finish_game(self):
		pass

	def is_alive(self, player):
		# not killed by engine (due to sandbox error or other bot malfunction) AND not dominated by other players
		return not self.killed[player] and self.active[player]

	def kill_player(self, player):
		self.killed[player] = True

	def over(self):
		# if game is decided before max_turns, should return True
		return False

	def get_score(self, player_id=None):
		if player_id == None:
			return self.scores
		return self.scores[player_id]

if __name__ == '__main__':
	opts = {"map" : "/home/ananya/gits/saber/test",
			"turntime"  : 1000,
			"loadtime"  : 1000,
			"bot_count" : 2}
	gg = Game(opts)
	print(gg.get_start())