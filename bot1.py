#!/usr/bin/env python

from Quantum import *
"""
Transpose BOT
"""

class myBot():
	
	def __init__(self):
		self.name = "transpose Bot"
		# any persistene data structures

	def do_setup(self, game):
		print(game.number_of_words)
		print(game.words)
		pass

	def do_turn(self, game):
		"""
		take transpose
		"""
		for i in range(0, game.number_of_words):
			r = ""
			for j in range(0, game.number_of_words):
				r += game.words[j][i]
			game.make_move(r)

if __name__ == '__main__':
	try:
		ServerStack.launch(myBot())
	except KeyboardInterrupt:
		print("Ctrl-C, bye!")