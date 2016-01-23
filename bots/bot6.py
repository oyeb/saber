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
		pass

if __name__ == '__main__':
	try:
		ServerStack.launch(myBot())
	except KeyboardInterrupt:
		print("Ctrl-C, bye!")