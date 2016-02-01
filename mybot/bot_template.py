#!/usr/bin/env python

from Quantum import *
# any other imports here

# METHODS PROVIDED BY Quantum.py
# 
# game.attack(source_id, sink_id, arate)
# game.update_link(source_id, sink_id, new_arate)
# game.withdraw(source_id, sink_id, split_ratio)
#
# HELPER METHODS
#
# game.error_dump(<string>)
# game.distance_between(server_id, server_id)
# 
# game.pretty_dump_alerts()
# game.pretty_dump_additions()
# game.pretty_dump_deletions()

class myBot():
	"""
	My BOT
	"""
	def __init__(self):
		self.name = "my Bot"
		# initialise any persistent data structures (if needed)
	
	def do_setup(self, game):
		# do some setup here.. maybe?
		pass

	def do_turn(self, game):
		# make a few moves here
		pass

	# you can add functions here.
	# def important_function(self, args..):

if __name__ == '__main__':
	try:
		ServerStack.launch(myBot())
	except KeyboardInterrupt:
		print("Ctrl-C, bye!")