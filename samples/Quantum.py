from __future__ import print_function
import sys
import traceback
import random
import time
import util

class UnkownGameStateParameter(Exception):
	def __init__(self, line=None, key=None):
		if line and key:
			msg = "Unrecognised format. Found this line, \"%s\"\nkey=\"%s\", is not understood or data format is wrong.\nSomething wrong with saber/quantum.py\n" % (line, key)
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
		self.turntime = 0
		self.loadtime = 0
		self.turn = 0

		self.active = True
		self.Clusters = {}
		self.Servers = []
	
	def setup(self, start_data):
		"""
		empty lines and lines without '~' are ignored
		"""
		lines = start_data.split('\n')
		for line in lines:
			try:
				key, data = line.strip().split('~')
			except ValueError:
				# this happens because of the last newline which results in lines.split('\n') to be == [... , '...', '']
				# and the last item cannot be unpacked into (key, data)
				continue
			if key == 'turn':
				self.turn = int(data)
			elif key == 'turntime':
				self.turntime = int(data)
			elif key == 'loadtime':
				self.loadtime = int(data)
			elif key == 'id':
				self.my_id = int(data)
			elif key == 'act_width':
				self._actual_width = float(data)
			elif key == 'aspect':
				self._aspect = float(data)
			elif key in 'ns' and key != 'ns':
				try:
					sid, x, y, reserve, invested, limit, owner = data.split()
					self.Servers.append(util.Server((float(x), float(y)), float(reserve) + float(invested), float(limit), float(owner), int(sid)))
					if int(owner) in self.Clusters.keys():
						self.Clusters[int(owner)].append(int(sid))
					else:
						self.Clusters[int(owner)] = [int(sid)]
				except:
					raise UnkownGameStateParameter(line, key)
			elif key == 'bot_count':
				self.bot_count = int(data) # number of other bots
			elif key == 'server_count':
				self.server_count = int(data) # number of other bots
			else:
				raise UnkownGameStateParameter(line, key)
		self.my_nodes    = self.Clusters[self.my_id]
		self.enemy_nodes = [server.index for server in self.Servers if server.owner != self.my_id and server.owner != -1]
		self.neutrals    = [server.index for server in self.Servers if server.owner == -1]

	def update_state(self, up_data):
		"""
		empty lines and lines without '~' are ignored
		"""
		lines = up_data.split('\n')
		_clusters = {}
		for line in lines:
			try:
				key, data = line.strip().split('~')
			except ValueError:
				# this happens because of the last newline which results in lines.split('\n') to be == [... , '...', '']
				# and the last item cannot be unpacked into (key, data)
				continue
			if key == 'turn':
				self.turn = int(data)
			elif key == 'score':
				self.score = float(data)
			elif key == 's':
				try:
					sid, reserve, invested, owner = data.split()
					self.Servers[int(sid)].sync(float(reserve), float(invested), int(owner))
					if int(owner) in _clusters.keys():
						_clusters[int(owner)].append(int(sid))
					else:
						_clusters[int(owner)] = [int(sid)]
				except:
					raise UnkownGameStateParameter(line, key)
			elif key == 'cd':
				try:
					a_sid, v_sid = data.split()
					del self.Servers[int(a_sid)].connections[int(v_sid)]
				except:
					raise UnkownGameStateParameter(line, key)
			elif key == 'cn':
				try:
					a_sid, v_sid, arate, fdist = data.split()
					a_sid, v_sid, arate, fdist = int(a_sid), int(v_sid), float(arate), float(fdist)
					self.Servers[a_sid].new_connection(v_sid, arate, fdist)
				except:
					raise UnkownGameStateParameter(line, key)
			elif key == 'c':
				try:
					a_sid, v_sid, arate, state, length = data.split()
					a_sid, v_sid, arate, state, length = int(a_sid), int(v_sid), float(arate), int(state), float(length)
					self.Servers[a_sid].connections[v_sid].sync(arate, state, length)
				except:
					raise UnkownGameStateParameter(line, key)
		self.Clusters = _clusters			
		self.my_nodes    = self.Clusters[self.my_id]
		self.enemy_nodes = [server.index for server in self.Servers if server.owner != self.my_id and server.owner != -1]
		self.neutrals    = [server.index for server in self.Servers if server.owner == -1]

	def dist_between(self, id1, id2):
		"""
		@brief      Computes (obviously, the shortest) distance between 2 servers(nodes)
		
		@param      self  game-state object
		@param      id1   id of server1
		@param      id2   id of server2
		
		@return     # of routers on the shortest path between the 2 given servers.
		"""
		p1 = self.Servers[id1].pos
		p2 = self.Servers[id2].pos
		return ( ((p1[0]-p2[0])*self._actual_width)**2 + ((p1[1]-p2[1])*self._actual_width/self._aspect)**2 )**0.5

	def attack(self, sid, arate):
		sys.stdout.write( "a %d %d %f\n" % (self.my_id, sid, arate) )
		sys.stdout.flush()

	def update_link(self, sid, arate):
		sys.stdout.write( "u %d %d %f\n" % (self.my_id, sid, arate) )
		sys.stdout.flush()

	def withdraw(self, sid, split):
		sys.stdout.write( "w %d %d %f\n" % (self.my_id, sid, split) )
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
					game_state.update_state(map_data)
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