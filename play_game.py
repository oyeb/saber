#!/usr/bin/env python
import traceback
import sys
import os
import time
import random
import argparse

import engine
import quantum

parser = argparse.ArgumentParser(description="Plays a single game among the given bots", add_help=True)
parser.add_argument("-m", "--map-file", dest="map", required=True,
					help="Name of the map-file")
parser.add_argument("-t", "--turns", dest="turns",
					default=5, type=int,
					help="Max. turns in a game")
parser.add_argument("--turn-time", dest="turntime",
					default="1000", type=int,
					help="Timeout for making a turn")
parser.add_argument("--load-time", dest="loadtime",
					default="1000", type=int,
					help="Timeout for initialisation")
parser.add_argument("--points", dest="points",
					default="1", type=int,
					help="Points awarded for survivng a round")
parser.add_argument("-b", dest="bot_list", action="store",
					required=True, type=str, nargs="+",
					help="List of bots")
parser.add_argument("-l", dest="log_path", action="store",
					required=True, type=str,
					help="Log Area")
args = parser.parse_args()
# print(args)

# run rounds:
# bots = list of paths to bot_files
# enumerate engine options
# enumerate game options
# game = quantum.Game(game_options) 
# make file decriptors for game level logs
# engine.run_game(game, bots, engine_options)
# do more logging

engine_options = {	"turntime" : args.turntime,
					"loadtime" : args.loadtime,
					"points" : args.points,
					"map" : args.map,
					"log_path" : args,log_path}

result = run_game(args.bot_list, engine_options)

print(result)