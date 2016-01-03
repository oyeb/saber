#!/usr/bin/env python

from Quantum import *

import random
"""
Column Swapper BOT
"""

class myBot():
	
	def __init__(self):
		self.name = "Column	Swapper Bot"
		# any persistent data structures

	def do_setup(self, game):
		pass

	def do_turn(self, game):
		c1, c2 = random.randint(0, game.number_of_words-1), random.randint(0, game.number_of_words-1)
		for r in range(0, game.number_of_words):
			game.swap(r, c1, r, c2)

if __name__ == '__main__':
	try:
		ServerStack.launch(myBot())
	except KeyboardInterrupt:
		print("Ctrl-C, bye!")