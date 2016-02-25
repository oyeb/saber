#!/usr/bin/env python

from Quantum import *
# any other imports here

# my_nodes
# enemy_nodes
# neutrals

class myBot():
	"""
	Frugal Bot
	"""
	def __init__(self):
		self.name = "my Bot"
		self.sm = {'making'       : 0,
					'connected'   : 1,
					'withdrawing' : 2,
					'headon'      : 3,
					'whostile'    : 4}

		self.ism = {0 : 'making',
					1 : 'connected',
					2 : 'withdrawing',
					3 : 'headon',
					4 : 'whostile'}
		self.CSPEED      = 3
		self.DCSPEED     = 6
		self.amult       = 3.0
		# initialise any persistent data structures (if needed)
		self.SHOW_CONNS = True

	def do_setup(self, game):
		self.get_closest_nodes(game)
		self.booked = {sid : 0 for sid in game.my_nodes}
		for mysid in self.closest_neutrals.keys():
			game.error_dump(str(mysid) + str(self.closest_neutrals[mysid]))
		for mysid in self.closest_enemies.keys():
			game.error_dump(str(mysid) + str(self.closest_enemies[mysid]))
		game.error_dump("---"*10)
		self.age = 15


	def do_turn(self, game):
		game.error_dump(str(game.turn)+"  \/\/\n"+"---"*10)
		game.pretty_dump_alerts()
		game.pretty_dump_additions()
		game.pretty_dump_deletions()
		# get conn_inv_map
		self.get_attacking_conns(game)
		# get closest nodes (neutrals might change!)
		self.get_closest_nodes(game)
		# update booked
		rem = []
		add = []
		for ting in self.booked.keys():
			if ting not in game.Clusters[game.my_id]:
				rem.append(ting)
		for mine in game.Clusters[game.my_id]:
			if mine not in self.booked.keys():
				add.append(mine)
		for itrem in rem:
			del self.booked[itrem]
		for itadd in add:
			self.booked[itadd] = 0
		# get all rates
		self.allrates = []
		for sid in range(game.server_count):
			self.allrates.append({'own' : self.get_rates(sid, game), 'ext' : self.get_ext_rates(sid, game)})
			self.allrates[-1]['dr'] = self.allrates[-1]['own'][0] + self.allrates[-1]['ext'][0]
			game.error_dump(self.allrates[-1])
		good_offence_moves = {i: [] for i in game.my_nodes}

		# protect my own!

		# check all connections
		for msid in game.my_nodes:
			for conn in game.Servers[msid].connections.values():
				if conn.victim in game.Clusters[game.my_id] and conn.state != self.sm['withdrawing']:
					# withdraw now!
					if self.allrates[conn.victim]['dr'] < 0:
						game.withdraw(msid, conn.victim, 0.8)
					else:
						game.withdraw(msid, conn.victim, 0.3)					
					self.booked[msid] -= conn.full_distance / 2 if conn.state == self.sm['headon'] else conn.full_distance
				if conn.state == self.sm['headon']:
					# should i update arate? withdraw?
					pass
				if conn.state == self.sm['connected']:
					if len(self.in_connected[conn.victim]) > 1:
						# others are also connected
						grace = game.Servers[conn.victim].power / (self.allrates[conn.victim]['dr'] + conn.arate*self.amult)
						if grace > 1:
							game.update_link(msid, conn.victim, 0)
						else:
							game.update_link(msid, conn.victim, 2)

		# hit NEW! victims
		# neutrals
		# ntrl_profits = {}
		# for victim in game.neutrals:
		# 	# choose neutral victim
		# 	ntrl_profits[victim] = []
		# 	candidates = [msid for msid in self.closest_enemies[victim] if msid in game.Clusters[game.my_id]]
		# 	for mcid in candidates:
		# 		# choose closest candidate
		# 		try:
		# 			# is mcid 'connected' to victim?
		# 			conn = game.Servers[mcid].connections[victim]
		# 			continue
		# 		except:
		# 			detail = {'pow' : game.Servers[mcid].power,
		# 						'dr' : self.allrates[mcid]['dr']}
		# 			detail['makers'] = self.analyse_making(victim, game)
		# 			detail['arate'] = 0
		# 			detail['time'] = game.dist_between(mcid, victim) / self.CSPEED
		# 			detail['cost'] = game.dist_between(mcid, victim)
		# 			ntrl_profits[victim].append( (mcid, detail) )
		# 	# pick cheapest move
		# 	ntrl_profits[victim].sort(key=lambda item: item[1]['cost'])
			
		# 	try:
		# 		# some move is possible...
		# 		move = ntrl_profits[victim][0]
		# 		mcid = move[0]
		# 		if self.allrates[victim]['dr'] < 0:
		# 			grace = game.Servers[victim].power / abs(self.allrates[victim]['dr'])
		# 			if grace > move[1]['time']:
		# 				on_hit_pow = game.Servers[victim].power + (move[1]['time'] * self.allrates[victim]['dr'])
		# 				time_to_kill = on_hit_pow / abs(self.allrates[victim]['dr'] - 1.0*self.amult)
		# 				kill_cost = time_to_kill * 1.0
		# 				if time_to_kill > 2:
		# 					# wait for more turns
		# 					ntrl_profits[victim] = (99999,"wait")
		# 				else:
		# 					# this move `can` be made in this turn
		# 					if move[1]['pow'] - self.booked[mcid] - move[1]['cost'] > 8 and game.Servers[mcid].reserve - move[1]['cost'] > 8:
		# 						ntrl_profits[victim] = (self.allrates[victim]['dr'], move[1]['cost'], kill_cost, mcid, victim)
		# 					else:
		# 						ntrl_profits[victim] = (999999, "no resource")
		# 			else:
		# 				# oops, too less time.
		# 				game.error_dump("too less time for %d (%f) need (%f)" % (victim, grace, move[1]['time']))
		# 				ntrl_profits[victim] = (999999,"no time")
		# 		else:
		# 			if move[1]['makers']:
		# 				# dr is soon to drop below zero
		# 				new_dr = self.allrates[victim]['dr'] - move[1]['makers'][0][1]*self.amult
		# 				grace_time = move[1]['makers'][0][0] # + (game.Servers[victim].power + (move[1]['makers'][0][0] * self.allrates[victim]['dr']) / (self.allrates[victim]['dr'] + move[1]['makers'][0][1]*self.amult))
		# 				if grace_time < move[1]['time']:
		# 					on_hit_pow = game.Servers[victim].power + (move[1]['time'] * self.allrates[victim]['dr']) + (move[1]['time'] - grace_time) * move[1]['makers'][0][1]*self.amult
		# 					time_to_kill = on_hit_pow / abs(self.allrates[victim]['dr'] - 1.0*self.amult - move[1]['makers'][0][1]*self.amult)
		# 				else:
		# 					on_hit_pow = game.Servers[victim].power + (move[1]['time'] * self.allrates[victim]['dr'])
		# 					time_to_kill = on_hit_pow / abs(self.allrates[victim]['dr'] - 1.0*self.amult)
		# 			else:
		# 				new_dr = self.allrates[victim]['dr']
		# 				on_hit_pow = game.Servers[victim].power + (move[1]['time'] * self.allrates[victim]['dr'])
		# 				time_to_kill = on_hit_pow / abs(self.allrates[victim]['dr'] - 1.0*self.amult)
		# 			kill_cost = time_to_kill * 1.0
		# 			if move[1]['pow'] - self.booked[mcid] - move[1]['cost'] > 8 and game.Servers[mcid].reserve - move[1]['cost'] > 8:
		# 				ntrl_profits[victim] = (new_dr/5, move[1]['cost'], kill_cost, mcid, victim)
		# 			else:
		# 				ntrl_profits[victim] = (999999, "no resource")
		# 			game.error_dump(ntrl_profits[victim])

		# 	except IndexError:
		# 		# no move possible for this victim!?
		# 		ntrl_profits[victim] = (999999, "no_move!")
		# 		continue
		# # only for neutrals
		# best_moves = sorted([ntrl_move for ntrl_move in ntrl_profits.values() if ntrl_move[0] < 500])
		# if best_moves:
		# 	_ , cost, kc, src, sink = best_moves[0]
		# 	good_offence_moves[src].append( (_, cost, kc, game.Servers[sink].power, sink) )
		
		# choose enemies
		enem_profits = {}
		for victim in game.enemy_nodes:
			# choose neutral victim
			enem_profits[victim] = []
			candidates = [msid for msid in self.closest_enemies[victim] if msid in game.Clusters[game.my_id]]
			for mcid in candidates:
				# choose closest candidate
				try:
					# is mcid 'connected' to victim?
					conn = game.Servers[mcid].connections[victim]
					continue
				except:
					detail = {'pow' : game.Servers[mcid].power,
							  'dr' : self.allrates[mcid]['dr']}
					detail['time'] = game.dist_between(mcid, victim) / self.CSPEED
					detail['dist'] = game.dist_between(mcid, victim)
					on_hit_pow = game.Servers[victim].power + (detail['time'] * self.allrates[victim]['dr'])
					time_to_kill = on_hit_pow / abs(self.allrates[victim]['dr'] - 1.0*self.amult)
					kill_cost = time_to_kill * 1.0
					detail['ttk'] = time_to_kill
					detail['kc'] = kill_cost
					enem_profits[victim].append( (mcid, detail) )
			# pick cheapest move
			enem_profits[victim].sort(key=lambda item: item[1]['dist'])
			game.error_dump("chose victim %d "%(victim) + str(enem_profits[victim]))
			try:
				# some move is possible...
				move = enem_profits[victim][0]
				mcid = move[0]
				if self.allrates[victim]['dr'] < 0:
					grace = game.Servers[victim].power / abs(self.allrates[victim]['dr'])
					if grace > move[1]['time']:
						if move[1]['ttk'] > 6:
							# wait for more turns
							enem_profits[victim] = (99999,"wait")
						else:
							# this move `can` be made in this turn
							if move[1]['pow'] - self.booked[mcid] - (move[1]['dist']+move[1]['kc']/2) > 8 and game.Servers[mcid].reserve - (move[1]['dist']+move[1]['kc']/2) > 8:
								enem_profits[victim] = (self.allrates[victim]['dr'], move[1]['dist'], move[1]['kc']/2, mcid, victim)
							else:
								enem_profits[victim] = (999999, "no_resource")
					else:
						# oops, too less time.
						game.error_dump("too less time for %d (%f) need (%f)" % (victim, grace, move[1]['time']))
						enem_profits[victim] = (999999,"no time")
				else:
					# dr > 0
					if move[1]['pow'] - self.booked[mcid] - (move[1]['dist']+move[1]['kc']/2) > 8 and game.Servers[mcid].reserve - (move[1]['dist']+move[1]['kc']/2) > 8:
						enem_profits[victim] = (self.allrates[victim]['dr'], move[1]['dist'], move[1]['kc']/2, mcid, victim)
					else:
						enem_profits[victim] = (999999, "no resource")
				game.error_dump("EN "+str(enem_profits[victim]))
			except IndexError:
				# no move possible for this victim!?
				enem_profits[victim] = (999999, "no_move!")
				continue
		best_moves = sorted([enem_move for enem_move in enem_profits.values() if enem_move[0] < 500])
		if best_moves:
			_ , dist, kc, src, sink = best_moves[0]
			good_offence_moves[src].append( (_, dist, kc, game.Servers[sink].power, sink) )

		# look at good_offence_moves now
		for msid in game.my_nodes:
			if good_offence_moves[msid]:
				good_offence_moves[msid].sort()
				dr, dist, kc, _pow, sink = good_offence_moves[msid][0]
				if dr > 0 and self.age > 0:
					self.age -= 1
				else:
					self.age = 18
					game.attack(msid, sink, 2.0)
					self.booked[msid] += dist

	def get_closest_nodes(self, game):
		cl_enemy = {}
		cl_neutral = {}
		for sid in range(game.server_count):
			other_enemy_nodes   = [osid for osid in range(game.server_count) if osid != sid and game.Servers[osid].owner != -1 and osid not in game.Clusters[game.Servers[sid].owner]]
			other_neutral_nodes = [osid for osid in range(game.server_count) if osid != sid and game.Servers[osid].owner == -1]
			game.error_dump("id:%d en:%r nn:%r"%(sid, other_enemy_nodes, other_neutral_nodes))
			cl_enemy[sid] = sorted(other_enemy_nodes, key=lambda esid: game.dist_between(sid, esid))
			cl_neutral[sid] = sorted(other_neutral_nodes, key=lambda esid: game.dist_between(sid, esid))
		self.closest_enemies = cl_enemy
		self.closest_neutrals = cl_neutral

	def get_attacking_conns(self, game):
		self.in_making = {sid: [] for sid in range(game.server_count)}
		self.in_connected = {sid: [] for sid in range(game.server_count)}
		self.in_headon = {sid: [] for sid in range(game.server_count)}
		self.in_whostile = {sid: [] for sid in range(game.server_count)}
		for sid1 in range(game.server_count):
			for sid2 in range(game.server_count):
				if sid1 == sid2:
					continue
				# get all conns from 2->1
				for conn in game.Servers[sid2].connections.values():
					if int(conn.victim) == sid1:
						if conn.state == self.sm['making']:
							self.in_making[sid1].append(sid2)
						elif conn.state == self.sm['connected']:
							self.in_connected[sid1].append(sid2)
						elif conn.state == self.sm['headon']:
							self.in_headon[sid1].append(sid2)
						elif conn.state == self.sm['whostile']:
							self.in_whostile[sid1].append(sid2)
		if self.SHOW_CONNS:
			game.error_dump("making      " + str(self.in_making))
			game.error_dump("connected   " + str(self.in_connected))
			game.error_dump("headon      " + str(self.in_headon))
			game.error_dump("whostile    " + str(self.in_whostile))

	def get_rates(self, sid, game):
		if game.Servers[sid].owner == -1:
			dr = 0
		else:
			dr = 0.8
		di = 0
		# see what this guy's actions are doing to itself
		for conn in game.Servers[sid].connections.values():
			if conn.state == self.sm['making']:
				di += self.CSPEED
				dr -= self.CSPEED
			if conn.state == self.sm['connected']:
				dr -= conn.arate
			if conn.state == self.sm['headon']:
				dr -= conn.arate
			# don't consider withdrawing as they go away too fast
			# if conn.state == self.sm['withdrawing']:
			# 	di -= self.DCSPEED
			# 	dr += self.DCSPEED
		return dr, di

	def get_ext_rates(self, vsid, game):
		dr =  0
		# see what others are doing to it (right now)
		for sid in self.in_connected[vsid]:
			conn = game.Servers[sid].connections[vsid]
			if sid in game.Clusters[game.Servers[vsid].owner]:
				# sid is in family of vsid
				dr += conn.arate
			else:
				dr -= conn.arate * self.amult
		for sid in self.in_headon[vsid]:
			conn = game.Servers[sid].connections[vsid]
			dr -= conn.arate * self.amult
		# don't consider 'whostile' as they go away too fast
		for sid in self.in_whostile[vsid]:
			if sid in game.Clusters[game.Servers[vsid].owner]:
				# sid is in family of vsid
				dr += self.DCSPEED
			else:
				dr -= self.DCSPEED
		return dr, 0

	def analyse_making(self, vsid, game):
		# what will happen in the future to this guy?
		makers = []
		for sid in self.in_making[vsid]:
			if sid not in game.Clusters[game.Servers[vsid].owner]:
				conn = game.Servers[sid].connections[vsid]
				makers.append( ((conn.full_distance - conn.length) / self.CSPEED, conn.arate, sid) )
		return sorted(makers)

if __name__ == '__main__':
	try:
		ServerStack.launch(myBot())
	except KeyboardInterrupt:
		print("Ctrl-C, bye!")