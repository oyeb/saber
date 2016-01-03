#!/usr/bin/env python

from Quantum import *

import random

class myBot():
	"""
	rotate-cipher bot
	"""
	def __init__(self):
		self.name = "Rotate Cipher Bot"
		# initialise any persistent data structures (if needed)

	def do_setup(self, game):
		self.delta = 26 - game.number_of_words
		self.turn = game.turn

	def do_turn(self, game):
		for i in range(1, random.randint(1, game.number_of_words)):
			r, c = random.randint(0, game.number_of_words-1), random.randint(0, game.number_of_words-1)
			new_ch = self.rotate(game.map[r][c])
			# print(r, c, new_ch, file=sys.stderr)
			game.edit(r, c, new_ch)

	def rotate(self, ch):
		return chr(ord('a') + (ord(ch) - ord('a') + self.delta) % 26)

if __name__ == '__main__':
	try:
		ServerStack.launch(myBot())
	except KeyboardInterrupt:
		print("Ctrl-C, bye!")