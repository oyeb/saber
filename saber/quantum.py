import random, math, json, copy

import map_util
import util

STATE_MAP = util.Connection.STATE_MAP
INV_ST_MAP = {0: 'making', 1: 'connected', 2: 'withdrawing', 3: 'headon', 4: 'whostile'}
VALID_ORDERS = {'a':('attack', 3),   # from, to, rate
				'w':('withdraw', 3), # from, to, split
				'u':('update', 3)}   # from, to, rate
class Game:
	def __init__(self, options, json_replay_list):
		# create map and get bot_count, server_count, etc from map_data
		self.mapfile = options["map"]
		self.map          = map_util.Map(self.mapfile)
		self.bot_count    = self.map.bot_count
		self.server_count = self.map.server_count

		self.max_turns = options["turns"]
		self.turntime  = options["turntime"]
		self.loadtime  = options["loadtime"]
		self.base_dir  = options["base_dir"]

		self.replay_list   = json_replay_list
		self.notify_logs   = None

		util.DEFAULT_REGEN = options["regen"]
		util.MAX_ARATE     = options["max_arate"]
		util.CSPEED        = options["cspeed"]
		util.DCSPEED       = options["dcspeed"]
		util.THRESHOLD     = options["threshold"]
		util.BONUS         = options["bonus"]
		util.REWARD        = options["reward"]
		self.amult         = options["amult"]
		self.score_pawn    = options["sc_pawn"]
		self.score_loss    = options["sc_loss"]
		self.EPOCH_COUNT   = options["epochs"]

	def start_game(self):
		self.Clusters = {}
		self.Servers = []
		sid = 0
		for owner in self.map.clusters.keys():
			for server in self.map.clusters[owner]:
				self.Servers.append(util.Server(server["coord"], server["power"], server["limit"], server["owner"], sid))
				if server["owner"] in self.Clusters.keys():
					self.Clusters[server["owner"]].append(sid)
				else:
					self.Clusters[server["owner"]] = [sid]
				sid += 1

		self.turn = 0
		self.scores = [0] * self.bot_count
		self.active = [True] * self.bot_count
		self.killed = [False] * self.bot_count # if True, it denotes that a bot malfunctioned and was killed by the system
		self.new_conns = []
		self.del_conns = []

	def get_start_json(self):
		res = { "act_width"    : self.map.actual_width,
				"aspect"       : self.map.aspect,
				"bot_count"    : self.bot_count,
				"servers"      : [],
				"clusters"     : self.Clusters,
				"max_turns"    : self.max_turns,
				"regen"        : util.DEFAULT_REGEN,
				"max_arate"    : util.MAX_ARATE,
				"threshold"    : util.THRESHOLD,
				"cspeed"       : util.CSPEED,
				"dcspeed"      : util.DCSPEED,
				"reward"       : util.REWARD,
				"sc_pawn"      : self.score_pawn,
				"sc_loss"      : self.score_loss,
				"amult"        : self.amult,
				"num_epochs"   : self.EPOCH_COUNT}
		for server in self.Servers:
			res['servers'].append({	"pos"         : server.pos,
									"reserve"     : server.reserve,
									"invested"    : server.invested,
									"owner"       : server.owner,
									"limit"       : server.limit,
									"connections" : []
								 })
		return json.dumps(res, sort_keys=True, separators=(',', ':'))

	def get_start_player(self, player=None, showmap = True):
		"""
		common start data
		"""
		# for the game_log here
		res = ["turn~0"]
		res.append("act_width~%f" % self.map.actual_width)
		res.append("aspect~%f" % self.map.aspect)
		res.append("turntime~%d" % self.turntime)
		res.append("loadtime~%d" % self.loadtime)
		res.append("bot_count~%d" % self.bot_count)
		res.append("server_count~%d" % self.server_count)
		# player specific data here
		if player != None:
			res.append("id~%d" % player)
		# map here
		for i, server in enumerate(self.Servers):
			if server.owner == -1:
				res.append("n~%d %s" % (i, server.strify())) # pos[0],pos[1], reserve, invested, limit, owner
			else:
				res.append("s~%d %s" % (i, server.strify())) # pos[0],pos[1], reserve, invested, limit, owner
		if player == None:
			if showmap:
				res.append(self.map.show(60))
				res.append("="*20)
		return '\n'.join(res)+'\n'

	def start_turn(self):
		self.turn += 1
		self.new_conns = []
		self.orders = [[] for i in range(self.bot_count)] # this is filled by do_moves

	def get_player_update(self, player_id):
		score_line = "score~%d\n" % self.scores[player_id]
		ser_lines = ""
		con_active_lines = ""
		con_ex_lines = ""
		notify_lines = ""
		for conn in self.del_conns:
			try:
				con_ex_lines += "cd~%d %d %d\n" % (conn[0], conn[1], conn[2])
			except TypeError:
				# these are 'whostile' connection objects that are created in case of a withdraw!
				con_ex_lines += "cd~%d '%s' %d\n" % (conn[0], conn[1], conn[2])
		for conn in self.new_conns:
			try:
				con_ex_lines += "cn~%d %d %f %f %d\n" % (conn[0], conn[1], conn[2], conn[3], conn[4]) # a_sid, v_sid, arate, full_distance, state
			except TypeError:
				# these are 'whostile' connection objects that are created in case of a withdraw
				con_ex_lines += "cn~%d '%s' %f %f %d\n" % (conn[0], conn[1], conn[2], conn[3], conn[4]) # a_sid, v_sid, arate, full_distance, state
		for server in self.Servers:
			ser_lines += "s~%s\n" % (server.up_strify()) # index, reserve, invested, owner
			for conn in server.connections.values():
				con_active_lines += "c~%s\n" % conn.up_strify() # attacker, victim, arate, state, length
		return (score_line + con_ex_lines + notify_lines + ser_lines + con_active_lines)

	def get_current_state(self, mode='log'):
		"""
		Used only for logging the game-level log
		"""
		if mode == 'log':
			res = "bots "
			for i in range(self.bot_count):
				res += "%2d:%s " % (i, str(self.is_alive(i)))
			score_line = "score " + ' '.join( map(str, self.scores) ) + '\n'
			ser_lines = ""
			con_lines = ""
			notify_lines = ""
			if self.notify_logs:
				for bot_notif in self.notify_logs:
					if bot_notif:
						for notice in bot_notif:
							notify_lines += "%s %s" % (notice[0], notice[2])
			for server in self.Servers:
				ser_lines += "%d %s\n" % (server.index, server)
				for conn in server.connections.values():
					con_lines += "%s\n" % conn
			return "%s\n%sNotifications\n%s\nClusters %r\nServers\n%sConnections\n%s_____\n" %(res, score_line, notify_lines, self.Clusters, ser_lines, con_lines)
		elif mode == 'json':
			res = { "turn"      : self.turn,
					"alive?"    : [self.is_alive(i) for i in range(self.bot_count)],
					"scores"    : self.scores[:],
					"servers"   : [],
					"clusters"  : copy.deepcopy(self.Clusters)}
			for server in self.Servers:
				conns = []
				for conn in server.connections.values():
					conns.append({	"src"    : conn.attacker,
									"sink"   : int(conn.victim),
									"arate"  : conn.arate,
									"length" : conn.length,
									"fdist"  : conn.full_distance,
									"state"  : conn.state
								})
				res['servers'].append({	"reserve"     : server.reserve,
										"invested"    : server.invested,
										"owner"       : server.owner,
										"connections" : conns
								 	})
			return res

	def parse_move(self, pid, move):
		"""
		parse the given moves-list-of-strings, only check if formatting and data-type is correct
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
			if data[0] == 'a':
				# attack
				if len(data[1:]) != VALID_ORDERS['a'][1]:
					invalid.append("%s {invalid formatting, or wrong # of args!}" % line)
				else:
					src_sid, sink_sid, rate = data[1:]
					# validate data-types
					try:
						a_sid = int(src_sid)
						v_sid = int(sink_sid)
						arate = float(rate)
						orders.append( ('a', (a_sid, v_sid, arate)) )
						valid.append(line)
					except:
						invalid.append("%s {Invalid `server_id` or `attack_rate`}" % line)
			elif data[0] == 'w':
				# withdraw
				if len(data[1:]) != VALID_ORDERS['w'][1]:
					invalid.append("%s {invalid formatting, or wrong # of args!}" % line)
				else:
					src_sid, sink_sid, split_r = data[1:]
					# validate data-types
					try:
						a_sid = int(src_sid)
						v_sid = int(sink_sid)
						split = float(split_r)
						orders.append( ('w', (a_sid, v_sid, split)) )
						valid.append(line)
					except:
						invalid.append("%s {Invalid `server_id` or `split_ratio`}" % line)
						continue
			elif data[0] == 'u':
				# update_link
				if len(data[1:]) != VALID_ORDERS['u'][1]:
					invalid.append("%s {invalid formatting, or wrong # of args!}" % line)
				else:
					src_sid, sink_sid, rate = data[1:]
					# validate data-types
					try:
						a_sid = int(src_sid)
						v_sid = int(sink_sid)
						arate = float(rate)
						orders.append( ('u', (a_sid, v_sid, arate)) )
						valid.append(line)
					except:
						invalid.append("%s {Invalid `server_id` or `attack_rate`}" % line)
						continue
			else:
				invalid.append("%s {Unknown Action!} [%s]" %(data[0], line))
		
		"""
		Now, we must validate these moves, by calling self.validate_moves()
		"""
		return self.validate_move(pid, orders, valid, invalid)

	def validate_move(self, pid, orders, valid, invalid):
		"""
		Valid move might turn into invalid or ignored ones.
		Check for out of bound map access and other illegal things here:

		* Out-Of-Bounds
		* attack_rate is out-of-range
		* Connection split not a ratio
		* In a set of commands, a victim server is reffered to, twice
		"""
		seen_locations = set() # can't daisy chain locations
		valid_orders   = []
		valid_lines    = []
		ignored        = []		
		for line, order in zip(valid, orders):
			if order[0] in 'awu':
				a_sid, v_sid, _ = order[1]
				# checks on SID below
				if a_sid not in self.Clusters[pid]:
					invalid.append("%s {Can't operate from enemy/neutral (see src_sid)!}" % line)
					continue
				elif v_sid in seen_locations:
					ignored.append("%s {Ignored this. >1 commands with same target-sid!}" % line)
					continue
				elif self.out_of_bounds(v_sid):
					invalid.append("%s {Invalid target-sid [IndexError]!}" % line)
					continue
				elif a_sid == v_sid:
					invalid.append("%s {Can't target self in this way! You gave `victim`==`attacker`!}" % line)
					continue
				else:
					seen_locations.add(order[1][0])
			# checks on ARATE, SPLIT_RATIO, CONNECTION_VALIDITY below
			if order[0] == 'a':
				a_sid, v_sid, arate = order[1]
				if (v_sid in self.Servers[a_sid].connections.keys()) and\
				   (self.Servers[a_sid].connections[v_sid].state != STATE_MAP['withdrawing']):
					# if connection to victim exists in ['making', 'connected', 'headon'], then
					ignored.append("%s {Ignored this. Already connected/connecting to %d from %d.}" % (line, v_sid, a_sid))
					continue
				if (v_sid in self.Clusters[a_sid]) and\
				   (a_sid in self.Servers[v_sid].connections.keys()) and\
				   (self.Servers[v_sid].connections[a_sid].state in (STATE_MAP['making'], STATE_MAP['connected'])):
					ignored.append("%s {Ignored this. Already connected from friendly server %d to %d(this). Disconnect and then retry.}" % (line, v_sid, a_sid))
					continue
				elif arate < 0 or arate > util.MAX_ARATE:
					invalid.append("%s {Invalid `attack_rate`. Acceptable[0, %f]}" % (line, util.MAX_ARATE))
					continue
			if order[0] == 'w':
				a_sid, v_sid, split_r = order[1]
				if v_sid not in self.Servers[a_sid].connections.keys():
					invalid.append("%s {No `connection` between %d and %d! First make a connection.}" % (line, a_sid, v_sid))
					continue
				elif split_r > 1.0 or split_r < 0:
					invalid.append("%s {Invalid `connection split` (ratio needed)!}" % line)
					continue
			if order[0] == 'u':
				a_sid, v_sid, split_r = order[1]
				if v_sid not in self.Servers[a_sid].connections.keys():
					invalid.append("%s {No `connection` between %d and %d! First make a connection.}" % (line, a_sid, v_sid))
					continue
				elif arate < 0 or arate > util.MAX_ARATE:
					invalid.append("%s {Invalid new `attack_rate`. Acceptable[0, %f]}" % (line, util.MAX_ARATE))
					continue
			valid_orders.append(order)
			valid_lines.append(line)
			seen_locations.add(order[1][1])

		return valid_orders, valid_lines, invalid, ignored

	def do_move(self, player_id, moves):
		# parse and validate moves
		orders, valid_lines, invalid_lines, ignored = self.parse_move(player_id, moves)
		# store this guy's orders here. This is reset @ self.start_turn()
		self.orders[player_id] = orders
		return valid_lines, invalid_lines, ignored

	def finish_turn(self):
		# implement valid commands
		error_list = [[] for j in range(self.bot_count)]
		self.implement_commands(error_list)
		self.do_epoch(error_list)
		# print("$$turn", self.turn)
		# print("##subtle_errors")
		# for pid, subtle_error in enumerate(error_list):
		# 	print(pid,":",subtle_error)
		self.notify_logs = error_list
	
	def implement_commands(self, error_list):
		for pid, _orders in enumerate(self.orders):
			if _orders:
				for mode, args in _orders:
					if mode == 'a':
						# make a new connection
						if args[0] in self.Servers[args[0]].connections.keys():
							# then this connection must be withdrawing!
							self.Servers[args[0]].connections[args[1]].state = STATE_MAP['making']
						else:
							# make new connection
							full_distance = self.dist_between(args[0], args[1])
							# determine _mode
							inv_conn = self.Servers[args[1]].connections.get(args[0], None)
							if inv_conn != None and inv_conn.state == STATE_MAP['connected']:
								# already being attacked by the "victim", make in 'headon' _mode
								check_length = full_distance / 2
								_mode = 'headon'
								# don't make inv_conn 'headon' here, as this request has not been fully validated yet.
							else:
								# make in 'normal' _mode, check if reserve >= fdist
								check_length = full_distance
								_mode = 'making'
							# if possible, make the connection
							if self.Servers[args[0]].reserve >= check_length:
								self.Servers[args[0]].new_connection(args[1], args[2], full_distance, STATE_MAP[_mode])
								self.new_conns.append((args[0], args[1], args[2], full_distance, STATE_MAP[_mode]))
								# make inv_conn 'headon' as well
								if inv_conn:
									inv_conn.state = STATE_MAP['headon']
							else:
								# not enuf reserve, notify user!
								message = "Can't attack %d from %d due to insufficient resource. Need %f" % (args[0], args[1], full_distance)
								error_list[pid].append(('i', 0.0, message))
					elif mode == 'w':
						conn = self.Servers[args[0]].connections[args[1]]
						full_distance = self.dist_between(args[0], args[1])
						_reward_length = (1 - args[2]) * conn.length
						if conn.state != STATE_MAP['making']:
							if conn.state == STATE_MAP['headon']:
								# opponent becomes 'making'
								inv_conn = self.Servers[args[1]].connections[args[0]]
								inv_conn.state = STATE_MAP['making']
							if _reward_length > 0.0001:
								# negligible rewards not given "bhaav"
								if args[1] in self.Clusters[args[0]]:
									# victim is friendly, don't do damage
									self.Servers[args[1]].new_connection(args[0], util.DCSPEED, full_distance, state=STATE_MAP['withdrawing'])
									self.Servers[args[1]].connections[args[0]].length = _reward_length
									self.new_conns.append((args[1], args[0], util.DCSPEED, full_distance, STATE_MAP['withdrawing']))
								else:
									# shoot the kuruvi, 'whostile's are owned by their creators, so that takeover detection is simple
									self.Servers[args[0]].new_connection(str(args[1]), util.DCSPEED/self.amult, full_distance, state=STATE_MAP['whostile'])
									# so why is the arate DCSPEED/amult. for normalisation of damages to determine "winner" in case of takeover
									self.Servers[args[0]].connections[str(args[1])].length = _reward_length
									self.new_conns.append((args[0], str(args[1]), util.DCSPEED/self.amult, full_distance, STATE_MAP['whostile']))
							# make myself 'withdrawing'
							conn.state = STATE_MAP['withdrawing']
							conn.length = (args[2] * conn.length)
							# also account the "reward-transaction" in 'invested'. Attend ECONOMICS 101, if you don't understand this
							self.Servers[args[0]].invested -= _reward_length
						else:
							# state was == 'making'
							conn.state = STATE_MAP['withdrawing']
					elif mode == 'u':
						conn = self.Servers[args[0]].connections[args[1]]
						conn.arate = args[2]
		return None

	def do_epoch(self, error_list):
		for epoch_id in range(self.EPOCH_COUNT):
			self.del_conns = []
			# inverse connection map, added even if connections are not entirely `made`, or in `withdrawing` state.
			# Also includes connections from owner-cluster
			self.inv_cmap = { i: [] for i in range(0, self.server_count)}
			for i in range(0, self.server_count):
				self.inv_cmap[str(i)] = []
			for server in self.Servers:
				for conn in server.connections.values():
					self.inv_cmap[conn.victim].append(conn.attacker)
			# update health
			for server in self.Servers:
				# apply regen only to non-neutrals which did not reach limits
				if server.owner != -1 and server.reserve < server.limit:
					server.update_pow(util.DEFAULT_REGEN / self.EPOCH_COUNT, 0)
					if server.reserve >= server.limit:
						server.reserve = server.limit
				# update the connection lengths of "this" server
				for v_sid in server.connections.keys():
					conn = server.connections[v_sid]
					# update their lengths
					if conn.state == STATE_MAP['making']:
						# check if there is an inv_conn that is also 'making'
						inv_conn = self.Servers[v_sid].connections.get(server.index, None)
						if inv_conn and inv_conn.state == STATE_MAP['making']:
							if inv_conn.length + conn.length > conn.full_distance:
								# both of them collided!!
								# set correct meeting point, don't care about cspeed
								overlap = inv_conn.length + conn.length - conn.full_distance
								conn.length     -= overlap / 2
								inv_conn.length -= overlap / 2
								# make them 'headon'
								conn.state     = STATE_MAP['headon']
								inv_conn.state = STATE_MAP['headon']
								server.update_pow(overlap/2, -overlap/2)
								self.Servers[v_sid].update_pow(overlap/2, -overlap/2)
							else:
								# not yet collided
								# extend both @cspeed/2
								increase = util.CSPEED / self.EPOCH_COUNT / 2
								conn.length += increase
								inv_conn.length += increase
								inv_conn.update_pow(-increase, increase)
								server.update_pow(-increase, increase)
						else:
							# no opponent connection (yet)
							if conn.length + (util.CSPEED / self.EPOCH_COUNT) > conn.full_distance:
								increase = (conn.full_distance - conn.length)
								conn.length = conn.full_distance
								conn.state = STATE_MAP['connected']
							else:
								increase = util.CSPEED / self.EPOCH_COUNT
								conn.length += increase
							server.update_pow(-increase, increase)
						# it's just now got 'connected' or 'headon', inflict damage in next epoch, not now.
					elif conn.state == STATE_MAP['withdrawing']:
						if conn.length - (util.DCSPEED / self.EPOCH_COUNT) < 0:
							self.del_conns.append((conn.attacker, v_sid, conn.state))
							server.update_pow(conn.length, -conn.length)
							# tell user the epoch number for exact time-of-death
						else:
							server.update_pow(util.DCSPEED / self.EPOCH_COUNT, -util.DCSPEED / self.EPOCH_COUNT)
							conn.length -= util.DCSPEED / self.EPOCH_COUNT
					elif conn.state == STATE_MAP['headon']:
						# these might need length updates
						if self.Servers[v_sid].connections[server.index].state != STATE_MAP['headon']:
							conn.state = STATE_MAP['making']
						if conn.length != 0.5 * conn.full_distance:
							mult = -1 if (0.5 * conn.full_distance - conn.length) < 0 else 1
							dist = min( (util.CSPEED / self.EPOCH_COUNT), abs(0.5 * conn.full_distance - conn.length) )
							conn.length += mult * dist
							server.update_pow(-mult * dist, mult * dist)
						# but servers need health updates
						server.update_pow(-conn.arate / self.EPOCH_COUNT, 0)
						self.Servers[v_sid].update_pow(-conn.arate * self.amult / self.EPOCH_COUNT, 0)
					elif conn.state == STATE_MAP['whostile']:
						if conn.length - (util.DCSPEED / self.EPOCH_COUNT) < 0:
							self.del_conns.append((conn.attacker, v_sid, conn.state))
							if int(v_sid) in self.Clusters[conn.attacker]:
								# it was successfully taken over by the attacker, now it's support time!
								self.Servers[int(v_sid)].update_pow(conn.length, 0)
							else:
								# attack until this vsid is not attacker's
								self.Servers[int(v_sid)].update_pow(-conn.length, 0)
						else:
							if int(v_sid) in self.Clusters[conn.attacker]:
								# it was successfully taken over by the attacker, now it's support time!
								self.Servers[int(v_sid)].update_pow(util.DCSPEED / self.EPOCH_COUNT, 0)
							else:
								# attack until this vsid is not attacker's
								self.Servers[int(v_sid)].update_pow(-(util.DCSPEED / self.EPOCH_COUNT), 0)
							conn.length -= util.DCSPEED / self.EPOCH_COUNT
					else:
						# already connected
						if v_sid in self.Clusters[server.owner]:
							# if friendly bot, don't inflict damage
							self.Servers[v_sid].update_pow(conn.arate / self.EPOCH_COUNT, 0)
						else:
							self.Servers[v_sid].update_pow(-conn.arate * self.amult / self.EPOCH_COUNT, 0)
						server.update_pow(-conn.arate / self.EPOCH_COUNT, 0)
			# delete the dead connection objects!!
			for dcon in self.del_conns:
				del self.Servers[dcon[0]].connections[dcon[1]]
				# also update the inverse-connection-map!!
				self.inv_cmap[dcon[1]].remove(dcon[0])
			
			# check takeovers
			for server in self.Servers:
				if server.power <= 0:
					# takeover is happening!!
					winner = self.Servers[self.determine_takeover(server.index)]
					message = "%d's %d pawned your server %d! @ turn(%d)+%2.4f" % (winner.owner, winner.index, server.index, self.turn, epoch_id/self.EPOCH_COUNT)
					error_list[server.owner].append(('p', epoch_id/self.EPOCH_COUNT, message))
					# award bonuses, ensure no race condition
					if server.owner == -1:
						server.update_pow(util.BONUS, 0)
					else:
						server.update_pow(util.REWARD, 0)
						self.scores[server.owner] -= self.score_loss
					self.scores[winner.owner] += self.score_pawn
					self.Clusters[server.owner].remove(server.index)
					self.Clusters[winner.owner].append(server.index)
					server.owner = winner.owner
					# withdraw all connections (if any)
					for conn in server.connections.values():
						conn.state = STATE_MAP['withdrawing']

			# validate connections,
			# remove a few if "in_danger"?
			for server in self.Servers:
				if server.owner == -1:
					continue
				if server.reserve < util.THRESHOLD:
					# in_danger!
					d_rate, s_rate, my_arates, _cspeeds, _dcspeeds, _making, _connected, _headons = self.get_power_rates(server.index, 'epoch')
					# _making and _connected have victim-server-ids
					dr = (util.DEFAULT_REGEN / self.EPOCH_COUNT + _dcspeeds + s_rate) - (d_rate*self.amult + my_arates + _cspeeds)
					# di = _cspeeds - _dcspeeds
					if dr < 0:
						# need to resolve, but withdraw only 1 connection in this epoch.
						# Next epoch will take another out, automatically.
						# choose the bakra connection, it's possible that such a connection doesn't exist
						bakra = None
						min_length = 999999999
						for v_sid in _making:
							if server.connections[v_sid].length < min_length:
								min_length = server.connections[v_sid].length
								bakra = v_sid
						if bakra == None and _connected:
							bakra = random.choice(_connected)
						elif _headons:
							bakra = random.choice(_headons)
						# still, you might not find a bakra
						if bakra:
							# found a bakra
							bakra_conn = server.connections[bakra]
							# notify user of this automatic, "uintended" operation
							message = "Server %d is \"in-danger\". Game 'auto-withdrew' connection to %d (state:'%s') @ turn(%d)+%2.4f" % (server.index, bakra_conn.victim, INV_ST_MAP[bakra_conn.state], self.turn, epoch_id/self.EPOCH_COUNT) 
							error_list[server.owner].append(('w', epoch_id/self.EPOCH_COUNT, message))
							# withdraw it!
							bakra_conn.state = STATE_MAP['withdrawing']
						else:
							# did not find bakra, leave this be.
							pass
			# update scores, ranks, determine dead bots, game endings
			for bid in self.Clusters.keys():
				if bid != -1 and len(self.Clusters[bid]) == 0:
					self.kill_player(bid)
			# add stuff in replay_list
			replay_epoch_elem = self.get_current_state(mode='json')
			replay_epoch_elem['epoch_id'] = epoch_id
			self.replay_list.append(replay_epoch_elem)
			# if self.turn in [54,55]:
			# 	for sid in range(self.server_count):
			# 		d_rate, s_rate, my_arates, _cspeeds, _dcspeeds, _making, _connected, _headons = self.get_power_rates(sid, 'epoch')
			# 		# _making and _connected have victim-server-ids
			# 		if self.Servers[sid].owner == -1:
			# 			dr = (_dcspeeds + s_rate) - (d_rate*self.amult + my_arates + _cspeeds)
			# 		else:
			# 			dr = (util.DEFAULT_REGEN/self.EPOCH_COUNT + _dcspeeds + s_rate) - (d_rate*self.amult + my_arates + _cspeeds)
			# 		di = _cspeeds - _dcspeeds
			# 		print("#sid%d:" % sid, dr, di, d_rate, s_rate, my_arates, _cspeeds, _dcspeeds)
			# 	print("t%2d-%2d\n"%(self.turn, epoch_id), self.get_current_state())

	def determine_takeover(self, sid):
		# find out attacker ids
		server = self.Servers[sid]
		normal_srcs = [sid for sid in self.inv_cmap[server.index] if sid not in self.Clusters[server.owner]]
		# also include 'whostile' connections to this server
		whostile_srcs = [sid for sid in self.inv_cmap[str(server.index)] if sid not in self.Clusters[server.owner]]
		max_arate = 0
		winner = None
		actual_enemies = []
		for src_id in normal_srcs:
			# is this guy even connected
			if self.Servers[src_id].connections[server.index].state in (STATE_MAP['headon'], STATE_MAP['connected']):
				actual_enemies.append(src_id)
				# what rate is this guy attacking me?
				src_arate = self.Servers[src_id].connections[server.index].arate
				if src_arate > max_arate:
					max_arate = src_arate
		if max_arate < util.DCSPEED/self.amult:
			# 'whostile' will win, DCSPEED requires normalisation, don't remove amult. You're dumb if you want to do that. Read code... and comments.
			# print("Yes, whostile did win this game", whostile_srcs)
			winner = random.choice(whostile_srcs)
		if not winner:
			# choose the top attackers
			winners = [sid for sid in actual_enemies if self.Servers[sid].connections[server.index].arate == max_arate]
			if len(winners) == 1:
				winner = winners[0]
			else:
				# recursive powers!
				winner = random.choice(winners)
		return winner

	def get_power_rates(self, sid, mode='real'):
		server = self.Servers[sid]
		# server == me
		sum_damage_rates = 0
		sum_support_rates = 0
		for enemy_id in self.inv_cmap[server.index]:
			enemy = self.Servers[enemy_id]
			if enemy.connections[server.index].state in ( STATE_MAP['connected'], STATE_MAP['headon'] ):
				# for "actively connected" ppl only
				if enemy.owner != server.owner:
					# for all enemies only
					sum_damage_rates += enemy.connections[server.index].arate
				else:
					# enemy is actually best friend
					sum_support_rates += enemy.connections[server.index].arate
		# check 'whostiles'
		for enemy_id in self.inv_cmap[str(server.index)]:
			enemy = self.Servers[enemy_id]
			if enemy.owner != server.owner:
				# for all enemies only
				sum_damage_rates += util.DCSPEED/self.amult # we are going to multiply sum_damage_rates with 'amult' anyways!
			else:
				# enemy is actually best friend
				sum_support_rates += util.DCSPEED # we are not going to multiply sum_support_rates with 'amult'!
		sum_arates = sum_cspeeds = sum_dcspeeds = 0
		_making    = []
		_connected = []
		_headons   = []
		for conn in server.connections.values():
			if conn.state == STATE_MAP['connected']:
				sum_arates +=  conn.arate
				_connected.append(conn.victim)
			elif conn.state == STATE_MAP['making']:
				sum_cspeeds += util.CSPEED
				_making.append(conn.victim)
			elif conn.state == STATE_MAP['headon']:
				sum_arates += conn.arate
				_headons.append(conn.victim)
			else:
				sum_dcspeeds += util.DCSPEED
		if mode == 'real':
			return (sum_damage_rates, sum_support_rates, sum_arates, sum_cspeeds, sum_dcspeeds, _making, _connected, _headons)
		elif mode == 'epoch':
			return (sum_damage_rates/self.EPOCH_COUNT,
					sum_support_rates/self.EPOCH_COUNT,
					sum_arates/self.EPOCH_COUNT,
					sum_cspeeds/self.EPOCH_COUNT,
					sum_dcspeeds/self.EPOCH_COUNT,
					_making,
					_connected,
					_headons)

	def finish_game(self):
		pass

	def is_alive(self, player):
		# not killed by engine (due to sandbox error or other bot malfunction) AND not dominated by other players
		# print("#", player, (not self.killed[player]) and self.active[player])
		return (not self.killed[player]) and self.active[player]

	def kill_player(self, player):
		self.killed[player] = True
		self.active[player] = False

	def over(self):
		# if game is decided before max_turns, should return True
		return False

	def get_scores(self, player_id=None):
		if player_id == None:
			return self.scores
		return self.scores[player_id]

	def out_of_bounds(self, sid):
		return sid < 0 or sid >= self.server_count

	def dist_between(self, id1, id2):
		"""
		@brief      Computes (obviously, the shortest) distance between 2 servers(nodes)
		
		@param      self  game-state object
		@param      id1   id of server1
		@param      id2   id of server2
		
		@return     # of routers on the shortest path between the 2 given servers.
		"""
		p1 = self.Servers[id1].pos
		p2 = self.Servers[id2].pos
		return ( ((p1[0]-p2[0])*self.map.actual_width)**2 + ((p1[1]-p2[1])*self.map.actual_width/self.map.aspect)**2 )**0.5

if __name__ == '__main__':
	opts = {"map" : "/home/ananya/gits/saber/maps/test.map",
			"turntime"  : 2,
			"loadtime"  : 2,
			"base_dir"  : "/home/ananya/gits/saber/",
			"cspeed"    : 3.0,
			"dcspeed"   : 6.0,
			"threshold" : 6,
			"epochs"    : 50,
			"bonus"     : 20,
			"reward"    : 6,
			"sc_pawn"   : 10,
			"sc_loss"   : 5,
			"max_arate" : 3.0,
			"regen"     : 0.8,
			"turns"     : 60,
			"amult"     : 3.0}

	gg = Game(opts, [])
	gg.start_game()
	print(gg.get_start_player(1))
	
	gg.start_turn()
	vo, inv, ig = gg.do_move(1, ["a 1 0 0.4000"]) #, "u 1 0 0.1", "u 1 4 0.2", "a 7 2 15", "u 1 1 0.7"])
	print(vo)
	print(inv)
	print(ig)
	gg.finish_turn()
	print("$$turn", gg.turn)
	print(gg.get_current_state())
	'''
	for i in range(0, 8):
		gg.start_turn()
		gg.do_move(0, [])
		gg.do_move(1, [])
		gg.finish_turn()
		#print("$$turn", gg.turn)
		#print(gg.get_current_state())
	'''
	for i in range(0, 60):
		gg.start_turn()
		if gg.turn == 12:
			gg.do_move(0, ["a 0 1 0.3"])
		else:
			gg.do_move(0, [])
		if gg.turn == 54:
			gg.do_move(1, ["w 1 0 0.4"])
		else:
			gg.do_move(1, [])
		gg.finish_turn()
		print("##orders:", gg.orders)
		for sid in range(gg.server_count):
			d_rate, s_rate, my_arates, _cspeeds, _dcspeeds, _making, _connected, _headons = gg.get_power_rates(sid, 'real')
			# _making and _connected have victim-server-ids
			if gg.Servers[sid].owner == -1:
				dr = (_dcspeeds + s_rate) - (d_rate*gg.amult + my_arates + _cspeeds)
			else:
				dr = (util.DEFAULT_REGEN + _dcspeeds + s_rate) - (d_rate*gg.amult + my_arates + _cspeeds)
			di = _cspeeds - _dcspeeds
			print("#sid%d:" % sid, dr, di, _making, _connected, _headons)
		print(gg.get_current_state())
	