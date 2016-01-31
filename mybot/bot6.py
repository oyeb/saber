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
		for i in range(game.server_count):
			game.error_dump("%d: %s" % (i, game.Servers[i]))

	def do_turn(self, game):
		if game.turn == 8:
			game.attack(0, 2, 0.3)
		if game.turn == 25:
			game.attack(0, 2, 0.4)
		if game.turn == 100:
			game.update_link(0, 2, 0.8)

if __name__ == '__main__':
	try:
		ServerStack.launch(myBot())
	except KeyboardInterrupt:
		print("Ctrl-C, bye!")