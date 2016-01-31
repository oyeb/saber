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
		if game.turn == 10:
			game.attack(1, 2, 0.4)
		elif game.turn == 20:
			game.withdraw(1, 2, 0.2)

if __name__ == '__main__':
	try:
		ServerStack.launch(myBot())
	except KeyboardInterrupt:
		print("Ctrl-C, bye!")