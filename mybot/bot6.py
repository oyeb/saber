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
		if game.turn == 41:
			game.attack(0,3,1)
			game.attack(0,2,1)
		if game.turn == 55:
			game.update_link(0,3,0.1)
			game.update_link(0,2,0.1)
		if game.turn == 56:
			game.attack(3,1,3)
			game.attack(2,1,3)
		if game.turn == 62:
			game.withdraw(0,2,0)
			game.withdraw(0,3,0)

		game.pretty_dump_alerts()
		game.pretty_dump_additions()
		game.pretty_dump_deletions()
		
		
if __name__ == '__main__':
	try:
		ServerStack.launch(myBot())
	except KeyboardInterrupt:
		print("Ctrl-C, bye!")