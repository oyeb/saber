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
		print(game.Clusters)
		print(game.my_id)
		print(game.__dict__)

	def do_turn(self, game):
		pass

if __name__ == '__main__':
	try:
		ServerStack.launch(myBot())
	except KeyboardInterrupt:
		print("Ctrl-C, bye!")