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
		self.base_dir = options["base_dir"]
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
		"""
		common start data
		"""
		# for the game_log here
		res = ["turn 0"]
		res.append("turntime %d" % self.turntime)
		res.append("loadtime %d" % self.loadtime)
		# player specific data here
		if player != None:
			res.append("bots %d" % (self.bot_count-1)) # number of other bots
		# map here
		for w in self.mapdata:
			res.append("m %s" % w)
		if player == None:
			res.append("="*20)
		return '\n'.join(res)+'\n'

	def start_turn(self):
		self.turn += 1
		self.orders = [[] for i in range(self.bot_count)] # this is filled by do_moves

	def get_player_update(self, player_id):
		score = "score %d\n" % self.scores[player_id]
		map_lines = 'm ' + '\nm '.join(self.mapdata) + '\n'
		return map_lines + score

	def get_current_state(self):
		"""
		Used only for logging the game-level log
		"""
		res = "bots "
		for i in range(self.bot_count):
			res += "%2d:%s " % (i, str(self.is_alive(i)))
		map_lines = 'm ' + '\nm '.join(self.mapdata) + '\n'
		score_line = "score " + ' '.join( map(str, self.scores) ) + '\n'
		return res+'\n' + map_lines + score_line + '_____\n'

	def parse_move(self, move):
		"""
		parse the given moves-string, only check if formatting and data-type is correct
		"""
		orders  = []
		valid   = []
		invalid = []
		for l in move:
			line = l.strip('\r\n').lower()
			# ignore blank lines or comments (Just in case some dumbass wants to debug via the stdout)
			if not line or line[0] == '#':
				continue
			data = line.split()
			if data[0] == 's':
				# swap
				if len(data[1:]) != VALID_ORDERS['s'][1]:
					invalid.append("%s {invalid formatting, or wrong # of args!}" % line)
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
					invalid.append("%s {invalid formatting, or wrong # of args!}" % line)
				else:
					r, c, ch = data[1:]
					# validate data-types
					try:
						loc = int(r), int(c)
					except:
						invalid.append("%s {Invalid `row` or `col`}" % line)
						continue
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
		return self.validate_move(orders, valid, invalid)

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
						self.mapdata[r] = self.mapdata[r][:c] + args[1] + self.mapdata[r][c+1:]
					if mode == 's':
						r1, c1 = args[0]
						r2, c2 = args[1]
						temp = self.mapdata[r1][c1]
						self.mapdata[r1] = self.mapdata[r1][:c1] + self.mapdata[r2][c2] + self.mapdata[r1][c1+1:]
						self.mapdata[r2] = self.mapdata[r2][:c2] +         temp         + self.mapdata[r2][c2+1:]
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

	def get_scores(self, player_id=None):
		if player_id == None:
			return self.scores
		return self.scores[player_id]

	def out_of_bounds(self, loc):
		r, c = loc
		if r < 0 or r > self.size-1 or c < 0 or c > self.size-1:
			return True
		return False

if __name__ == '__main__':
	opts = {"map" : "/home/ananya/gits/saber/maps/small_map.map",
			"turntime"  : 2,
			"loadtime"  : 2,
			"bot_count" : 2,
			"base_dir"  : "/home/ananya/gits/saber/"}
	gg = Game(opts)
	print(gg.get_start_player())

	gg.start_game()
	gg.start_turn()
	move = ["w pofa", "s 0 0    1 1", "e 5 1 h", "e 4 4 k l", "   e 7 3 5", "e j k l", "s e 4 3 2", "e 4 3", "   E          2 2 asd           "]
	a, b, c = gg.do_move(0, move)
	print()
	print(a)
	print(b)

	gg.finish_turn()
	print(gg.get_current_state())

	print(gg.get_player_update(1))