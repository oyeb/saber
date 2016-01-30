#!/usr/bin/env python

from Quantum import *
# any other imports here

class myBot():
	"""
	valid BOT
	"""
	def __init__(self):
		self.name = "valid Bot"
		# initialise any persistent data structures (if needed)
	
	def do_setup(self, game):
		self.gs = game
		self.closest = self.get_closest_nodes(game.my_nodes[0])

	def do_turn(self, game):
		if game.turn == 1:
			game.attack(2, 0.4)
		elif game.turn == 24:
			game.update_link(2, 0.1)
		elif game.turn == 26:
			game.withdraw(2, 1.0)

	def get_closest_nodes(self, src_index):
		sid_dist = []
		for sid in self.gs.neutrals + self.gs.enemy_nodes:
			sid_dist.append((self.gs.dist_between(src_index, sid), sid))
		return sorted(sid_dist, key=lambda dist: dist[0])

if __name__ == '__main__':
	try:
		ServerStack.launch(myBot())
	except KeyboardInterrupt:
		print("Ctrl-C, bye!")