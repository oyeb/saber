#!/usr/bin/env python
import traceback
import sys
import os
import datetime
import random
from configparser import ConfigParser
import json

import engine
import quantum

"""
All paths must be relative
"""
print("CWD", os.getcwd(), '\n')

parser = ConfigParser()
if getattr( sys, 'frozen', False ) :
        parser.read("saber/engine_settings.ini")
else :
        parser.read("engine_settings.ini")
engine_options = {	"turntime"    : float,
					"loadtime"    : float,
					"epochs"      : int,
					"threshold"   : int,
					"log_dir"     : str,
					"map_dir"     : str,
					"mybot_dir"   : str,
					"sample_dir"  : str,
					"json_logdir" : str,
					"arena"       : str,
					"user_cfg"    : str,
					"base_dir"    : os.getcwd(),
					"game_id"     : "LOCAL_GAME",
					"turns"       : None}
for option in parser.options('Engine'):
		engine_options[option] = engine_options[option](parser.get('Engine', option))

game_options = {"turntime"  : engine_options["turntime"],
				"loadtime"  : engine_options["loadtime"],
				"turns"     : engine_options["turns"],
				"base_dir"  : os.getcwd(),
				"epochs"    : engine_options["epochs"],
				"threshold" : engine_options["threshold"],
				"cspeed"    : float,
				"dcspeed"   : float,
				"max_arate" : float,
				"regen"     : float,
				"amult"     : float,
				"sc_pawn"   : float,
				"sc_loss"   : float,
				"bonus"     : int,
				"reward"    : int,}
for option in parser.options('Game'):
	game_options[option] = game_options[option](parser.get('Game', option))

sample_bot_names = ["donothing", "hard_coded", "special"]
sample_bots = [ {"version" : "3.5",
				 "fname"   : "donothing.py",
				 "cmd"     : None},
				{"version" : "3.5",
				 "fname"   : "hard_coded.py",
				 "cmd"     : None},
				 {"version" : "3.5",
				  "fname"   : "special.py",
				  "cmd"     : None}]

sample_dir = os.path.join(engine_options["base_dir"], engine_options["sample_dir"])
for bot in sample_bots:
	if int( bot['version'].split('.')[0] ) == 2:
		bot['cmd'] = "python2 %s" % os.path.join( sample_dir, bot['fname'])
	else:
		bot['cmd'] = "python %s" % os.path.join( sample_dir, bot['fname'])

parser.read(engine_options["user_cfg"])
game_options['turns'] = engine_options['turns'] = int(parser.get('sample', 'turns'))
mapfile = parser.get('map', 'mapfile')
map_dir = os.path.join( os.getcwd(), engine_options["map_dir"] )
game_options["map"] = os.path.join(map_dir, mapfile)

json_replay_list = []
json_notifications = []
game = quantum.Game(game_options, json_replay_list, json_notifications) #, json_notifications)

mybot_dir = os.path.join(engine_options["base_dir"], engine_options["mybot_dir"])
mybot = {	"fname"   : parser.get('mybot', 'name'),
			"version" : parser.get('mybot', 'version')}
if int( mybot['version'].split('.')[0] ) == 2:
	mybot['cmd'] = "python2 %s" % os.path.join( mybot_dir, mybot['fname'])
else:
	mybot['cmd'] = "python %s" % os.path.join( mybot_dir, mybot['fname'])

use_case = parser.get('sample', 'use')
if use_case != 'none':
	if use_case != 'all':
		allow = use_case.split(',')
		for fspec in allow:
			if fspec not in sample_bot_names:
				raise RuntimeError("\nThe file \"%s\" is not recognised by saber!\nPlease check `use` in `config.ini`" % fspec)
		allowed = []
		for i in range(0, len(sample_bots)):
			if sample_bots[i]['fname'].split('.')[0] in allow:
				allowed.append(sample_bots[i])
	else:
		allowed = sample_bots
	num_sample = len(allowed)
	num_reqd   = game.bot_count - 1
	# spread evenly
	needs = [num_reqd//num_sample+1]*(num_reqd%num_sample) + [num_reqd//num_sample]*(num_sample - num_reqd%num_sample)
	random.shuffle(needs)
	# choose the cluster_id 'chance' no. of times for the i^th sample_bot
	available = [k for k in range(1, game.bot_count)]
	bot_details = [None] * game.bot_count

	for samp_bot_id, chances in enumerate(needs):
		for _ in range(0, chances):
			bid = random.choice(available)
			available.remove(bid)
			bot_details[bid] = allowed[samp_bot_id]
else:
	bot_details = [mybot for _ in range(game.bot_count)]

# setup MyBot!
bot_details[0] = mybot
"""
for i, bot in enumerate(bot_details):
	print(i, bot)
"""

print("-"*80)
print("# of bots in Map '%s' is %d" % (mapfile, game.bot_count))
print("Your script, `%s` is dubbed `bot0` {id = 0} in this game." % mybot['fname'])
for i, bot in enumerate(bot_details):
	print("bot%2d is %s" % (i, bot['fname']))
print("-"*80 + '\n')
print("DEBUG")
print("=====")

if not os.path.exists(engine_options["log_dir"]):
	os.mkdir(engine_options["log_dir"])
if not os.path.exists(engine_options["arena"]):
	os.mkdir(engine_options["arena"])
if not os.path.exists(engine_options["json_logdir"]):
	os.mkdir(engine_options["json_logdir"])
engine_options["game_log"] = open( os.path.join( engine_options["log_dir"], "game_log.r%d.log" % 0), 'w' ) # round 0

result, json_start, json_end, json_mybot_ipstream, json_mybot_invalid, json_mybot_ignored, json_mybot_valid = engine.run_game(game, bot_details, engine_options)
# json_replay_list is also ready,
# jsonize it
json_replay = json.dumps(json_replay_list, separators=(',', ':'))
jnotify     = json.dumps(json_notifications, separators=(',', ':'))
# do more logging
if os.path.exists(engine_options["json_logdir"]):
	json_data_dump = open( os.path.join( engine_options["json_logdir"], "game_replay.js"), 'w' )
	json_data_dump.write("GAME_START=%s;\nGAME_REPLAY=%s;\nMYBOT_IP_STREAM=%s;\nMYBOT_INV_STREAM=%s;\nMYBOT_IGN_STREAM=%s;\nMYBOT_VAL_STREAM=%s\nGAME_END=%s;\nGAME_NOTIFICATIONS=%s;\n" % (json_start, json_replay, json_mybot_ipstream, json_mybot_invalid, json_mybot_ignored, json_mybot_valid, json_end, jnotify))
	json_data_dump.close()

print()
for k in result.keys():
	print(k, ':', result[k])

# close FDs!
engine_options["game_log"].close()

print("\nDONE\n" + "="*4)
print("You can see the logs in `logs` and visualise the game by running `game-ui/view_game.html` in your browser!")