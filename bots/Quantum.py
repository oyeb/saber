import sys
import traceback
import random
import time
from math import sqrt

class UnkownGameStateParameter(Exception):
	def __init__(self, line=None, key=None):
		if line and key:
			msg = "Unrecognised format. Found this line, \"%s\"\nkey=\"%s\", is not understood.\nSomething wrong with saber/quantum.py\n" % (line, key)
			print(msg, file=sys.stderr)
		else:
			print("Unrecognised format.\n", file=sys.stderr)
		raise RuntimeError

class ServerStack():
	"""
	Actual game-state as seen by "this" ServerStack
	"""
	def __init__(self):
		# all state variable, rows, cols, nodes, etc
		self.map = []
		self.turntime = 0
		self.loadtime = 0
		self.turn = 0

		self.active = True
	
	def setup(self, start_data):
		"""
		Each line must have 2 words, else line is ignored.
		"""
		lines = start_data.split('\n')
		for line in lines:
			try:
				key, data = line.strip().split()
			except ValueError:
				# this happens because of the last newline which results in lines.split('\n') to be == [... , '...', '']
				# and the last item cannot be unpacked into (key, data)
				continue
			if key == 'turn':
				self.turn = data
			elif key == 'turntime':
				self.turntime = data
			elif key == 'loadtime':
				self.loadtime = data
			elif key == 'm':
				self.map.append(data)
			elif key == 'bots':
				self.competitors = data # number of other bots
			else:
				raise UnkownGameStateParameter(line, key)
		self.number_of_words = len(self.map)

	def update(self, lines):
		"""
		Each line can have 1 or 2 words, else line is ignored.
		Additionally, if it has only one word, that word must == "end", else this line is ignored too.
		"""
		for line in lines.split('\n'):
			index = 0 # row_index of the map
			line = line.strip().split()

			if len(line) == 2:
				key, data = line
				if key == 'm':
					self.map[index] = data
					index += 1
				elif key == 'score':
					self.score = data
				elif key == 'turn':
					self.turn = data
				else:
					raise UnkownGameStateParameter(line, key)
			elif len(line) == 1:
				if line[0] == 'end':
					self.active = False
					# do antim sanskar
					break
				else:
					continue

	def edit(self, r, c, ch):
		sys.stdout.write( "e %d %d %c\n" % (r, c, ch) )
		sys.stdout.flush()

	def swap(self, r1, c1, r2, c2):
		sys.stdout.write( "s %d %d %d %d\n" % (r1, c1, r2, c2) )
		sys.stdout.flush()

	# helper functions
	
	@staticmethod
	def launch(bot=None):
		game_state = ServerStack()
		map_data = ''
		while game_state.active:
			try:
				cline = sys.stdin.readline().rstrip('\n\r')
				if cline == "":
					continue
				elif cline == 'ready':
					game_state.setup(map_data)
					if bot:
						bot.do_setup(game_state)
					sys.stdout.write("go\n")
					sys.stdout.flush()
					map_data = ''
				elif cline == "go":
					game_state.update(map_data)
					if bot and game_state.active:
						bot.do_turn(game_state)
					sys.stdout.write("go\n")
					sys.stdout.flush()
					map_data = ''
				else:
					map_data += cline + '\n'
			except EOFError:
				break
			except KeyboardInterrupt:
				raise
			except:
				traceback.print_exc(file=sys.stderr)
				sys.stderr.flush()

if __name__ == '__main__':
	ss = ServerStack()
	ss.launch(None)