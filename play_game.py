#!/usr/bin/env python
import traceback
import sys
import os
import time
import random
import argparse

import engine
import quantum

"""
All paths must be relative
"""

parser = argparse.ArgumentParser(description="Plays a single game among the given bots", add_help=True)
parser.add_argument("-m", "--map-file", dest="map", required=True,
					help="Name of the map-file")
parser.add_argument("-t", "--turns", dest="turns",
					default=5, type=int,
					help="Max. turns in a game")
parser.add_argument("-tt", "--turn-time", dest="turntime",
					default="3", type=int,
					help="Timeout for making a turn")
parser.add_argument("-ld", "--load-time", dest="loadtime",
					default="3", type=int,
					help="Timeout for initialisation")
parser.add_argument("--points", dest="points",
					default="1", type=int,
					help="Points awarded for survivng a round.")
parser.add_argument("-b", dest="bot_list", action="store",
					required=True, type=str, nargs="+",
					help="List of bots")
parser.add_argument("-l", dest="log_path", action="store",
					required=True, type=str,
					help="Log Area path. This must be a relative path!")
parser.add_argument("-a", dest="arena", action="store",
					required=True, type=str, default='arena',
					help="Arena, where the sanboxes are run. This must be a relative path.")
args = parser.parse_args()
# print(args)

# run rounds:
# bots = list of paths to bot_files
# enumerate engine options
engine_options = {	"turntime" : args.turntime,
					"loadtime" : args.loadtime,
					"points"   : args.points,
					"map"      : os.path.join( os.getcwd(), args.map),
					"log_dir"  : os.path.join( os.getcwd(), args.log_path ),
					"arena"    : os.path.join( os.getcwd(), args.arena ),
					"turns"    : args.turns,
					"base_dir"      : os.getcwd()}

# enumerate game options
game_options = {"map"       : engine_options["map"],
				"turntime"  : args.turntime,
				"loadtime"  : args.loadtime,
				"bot_count" : len(args.bot_list),
				"base_dir"       : os.getcwd()}

# make file decriptors for game level logs
if not os.path.exists(engine_options["log_dir"]):
	os.mkdir(engine_options["log_dir"])
engine_options["game_log"] = open( os.path.join( engine_options["log_dir"], "game_log.r%d" % 0), 'w' ) # round 0

# game = quantum.Game(game_options) 
game = quantum.Game(game_options)


result, replay_json = engine.run_game(game, args.bot_list, engine_options)

# do more logging
print(result)
print(replay_json)

# close FDs!
engine_options["game_log"].close()