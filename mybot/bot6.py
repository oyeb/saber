#!/usr/bin/env python

from Quantum import *
# any other imports here

class myBot():
	"""
	My BOT
	"""
	def __init__(self):
		self.name = "my Bot"
		# initialise any persistent data structures (if needed)
	
	def do_setup(self, game):
		pass

	def do_turn(self, game):
		if game.turn==4:
			game.attack(0, 3, 0.6)
		if game.turn==23:
			game.withdraw(0, 3, 0.5)
			game.attack(3, 1, 0.8)
		if game.turn==70:
			game.withdraw(3, 1, 0.7)
		game.pretty_dump_alerts()
		game.pretty_dump_additions()
		game.pretty_dump_deletions()
		for conn in game.Servers[3].connections.values():
			game.error_dump(conn)
if __name__ == '__main__':
	try:
		ServerStack.launch(myBot())
	except KeyboardInterrupt:
		print("Ctrl-C, bye!")