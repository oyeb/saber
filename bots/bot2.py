#!/usr/bin/env python

import Quantum
"""
Rotate BOT
"""

class myBot():
	
	def __init__(self):
		self.name = "RotateCipher Bot"
		self.delta = 0
		# any persistene data structures

	def do_setup(self, game):
		self.delta = 26 - game.number_of_words

	def do_turn(self, game):
		"""
		rotate each letter by "self.delta"
		"""
		for w, i in zip(game.words, range(0, game.number_of_words)):
			r = ""
			for j in range(0, game.number_of_words):
				index = ord(w[j])
				if w[j].islower():
					r += chr( 97 + (index+self.delta - 97)%26 )
				else:
					r += chr( 65 + (index+self.delta - 65)%26 )
			game.make_move(r)

if __name__ == '__main__':
	try:
		Quantum.ServerStack.launch(myBot())
	except KeyboardInterrupt:
		print("Ctrl-C, bye!")