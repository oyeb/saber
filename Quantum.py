import sys
import traceback
import random
import time
from math import sqrt

class ServerStack():
	"""
	Actual game-state as seen by "this" ServerStack
	"""
	def __init__(self):
		self.words = []
		self.number_of_words = 0
		# all state variable, rows, cols, nodes, etc
	
	def setup(self, map_data):
		lines = map_data.split('\n')[:-1]
		self.number_of_words = len(lines)
		for line in lines:
			self.words.append(line)

	def update(self, data):
		if data != "":
			words = data.split('\n')
			for i in range(0, self.number_of_words):
				self.words[i] = words[i]

	def make_move(self, move):
		sys.stdout.write("m %s\n"%move)
		sys.stdout.flush()

	# helper functions
	
	@staticmethod
	def launch(bot):
		game_state = ServerStack()
		map_data = ''
		while True:
			try:
				cline = sys.stdin.readline().rstrip('\n\r')
				if cline == 'ready':
					game_state.setup(map_data)
					bot.do_setup(game_state)
					sys.stdout.write("go\n")
					sys.stdout.flush()
				elif cline == "go":
					game_state.update(map_data)
					bot.do_turn(game_state)
					sys.stdout.write("go\n")
					sys.stdout.flush()
				else:
					map_data += cline + '\n'
			except EOFError:
				break
			except KeyboardInterrupt:
				raise
			except:
				traceback.print_exc(file=sys.stderr)
				sys.stderr.flush()