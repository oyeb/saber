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
		if game.turn == 15:
			game.attack(1, 0, 0.4)
		if game.turn == 36:
			game.withdraw(1, 0, 0.3)

		game.pretty_dump_alerts()
		game.pretty_dump_additions()
		game.pretty_dump_deletions()

if __name__ == '__main__':
	try:
		ServerStack.launch(myBot())
	except KeyboardInterrupt:
		print("Ctrl-C, bye!")