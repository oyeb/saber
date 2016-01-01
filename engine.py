import time
import traceback
import os
import random
import sys

from house import House

def run_game(game, bots, options):
	# instantiate logs
	# prepare list of bots (houses)
	# make sure the houses are all functioning
	# for turns ...
		# if turn == 0, start game
			# send game state to all
		# else
			# send updates to all
		# get moves from all. Wait till timeout. Do bots run in parallel?
		# process moves (game.do_moves)
		# remove eliminated bots
	# end game
	# consolidate game result
