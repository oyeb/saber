#!/usr/bin/env python
import traceback
import pprint
import sys
import os
import datetime
import random
import argparse
import json

import engine
import quantum

"""
All paths must be relative
"""

parser = argparse.ArgumentParser(description="Plays a single game among the given bots", add_help=True)

engine_spec = parser.add_argument_group('engine specific options')
engine_spec.add_argument("-gi", "--game-id", dest="game_id",
					default="boo",
					help="GAME-ID, needs to be unique and forever increasing.")
engine_spec.add_argument("-m", "--map-file", dest="map", required=True,
					help="Name of the map-file")
engine_spec.add_argument("-t", "--turns", dest="turns",
					default=5, type=int,
					help="Max. turns in a game")
engine_spec.add_argument("-tt", "--turn-time", dest="turntime",
					default="3", type=int,
					help="Timeout for making a turn")
engine_spec.add_argument("-ld", "--load-time", dest="loadtime",
					default="3", type=int,
					help="Timeout for initialisation")
engine_spec.add_argument("--points", dest="points",
					default="1", type=int,
					help="Points awarded for survivng a round.")
engine_spec.add_argument("-b", dest="bot_list", action="store",
					required=True, type=str, nargs="+",
					help="List of bots")
engine_spec.add_argument("-l", dest="log_path", action="store",
					required=True, type=str,
					help="Log Area path. This must be a relative path!")
engine_spec.add_argument("-a", dest="arena", action="store",
					required=True, type=str, default='arena',
					help="Arena, where the sanboxes are run. This must be a relative path.")

game_spec = parser.add_argument_group('game specific options')
game_spec.add_argument('-cs', '--cspeed', dest='cspeed',
						default=5, type=int,
						help='Connection speed. (routers/turn)')
game_spec.add_argument('-dcs', '--dcspeed', dest='dcspeed',
						default=10, type=int,
						help='dis-connection speed. (routers/turn)')
game_spec.add_argument('-ar', '--max_arate', dest='max_arate',
						default=5, type=float,
						help='Max Attack Rate on a connection (qubits/turn)')
game_spec.add_argument('-rg', '--regen', dest='regen',
						default=0.8, type=float,
						help='Regeneration Rate of each node. (qubits/turn)')
game_spec.add_argument('-am', '--amult', dest='amult',
						default=3.2, type=float,
						help='Attack multiplier. (3.0 to 4.0)')
args = parser.parse_args()
# print(args)

# run rounds:
# bots = list of paths to bot_files
# enumerate engine options
engine_options = {	"game_id"   : args.game_id,
					"turntime"  : args.turntime,
					"loadtime"  : args.loadtime,
					"points"    : args.points,
					"map"       : os.path.normpath( os.path.join( os.getcwd(), args.map)),
					"log_dir"   : os.path.normpath( os.path.join( os.getcwd(), args.log_path )),
					"arena"     : os.path.normpath( os.path.join( os.getcwd(), args.arena )),
					"turns"     : args.turns,
					"base_dir"  : os.getcwd(),
					"bot_count" : len(args.bot_list)}

# enumerate game options
game_options = {"map"       : engine_options["map"],
				"turntime"  : args.turntime,
				"loadtime"  : args.loadtime,
				"turns"     : args.turns,
				"bot_count" : len(args.bot_list),
				"base_dir"  : os.getcwd(),
				"cspeed"    : args.cspeed,
				"dcspeed"   : args.dcspeed,
				"max_arate" : args.max_arate,
				"regen"     : args.regen,
				"amult"     : args.amult}

# make file decriptors for game level logs
if not os.path.exists(engine_options["log_dir"]):
	os.mkdir(engine_options["log_dir"])
if not os.path.exists(engine_options["arena"]):
	os.mkdir(engine_options["arena"])
engine_options["game_log"] = open( os.path.join( engine_options["log_dir"], "game_log.r%d.log" % 0), 'w' ) # round 0

# game = quantum.Game(game_options) 
game = quantum.Game(game_options)

result, json_start, json_replay, json_end = engine.run_game(game, args.bot_list, engine_options)

# do more logging
json_data_dump = open( os.path.join( engine_options["log_dir"], "game_start.json"), 'w' )
json_data_dump.write(json_start)
json_data_dump.close()
json_data_dump = open( os.path.join( engine_options["log_dir"], "game_replay.json"), 'w' )
json_data_dump.write(json_replay)
json_data_dump.close()
json_data_dump = open( os.path.join( engine_options["log_dir"], "game_end.json"), 'w' )
json_data_dump.write(json_end)
json_data_dump.close()

print()
print(result)
'''
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(json.loads(json_replay))
#print(json_replay)
'''

# close FDs!
engine_options["game_log"].close()
