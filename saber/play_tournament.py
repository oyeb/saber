#!/usr/bin/env python
import traceback
import sys
import os, shutil
import datetime
import random
from configparser import ConfigParser
import argparse
import json
import uuid, itertools, pymysql
import engine
import quantum
import leaders

DEBUG = False
SHOW_ASSIGNMENT = True
SHOW_RESULT = True
random.seed()

def insert_safely(cursor, myquery):
	try:
		cursor.execute(myquery)
		return True
	except (pymysql.err.IntegrityError, pymysql.err.ProgrammingError) as e:
		if DEBUG:
			print("-<|WARNING|>- Skipped an insert as %s"%e)
		return False

"""
All paths must be relative
"""
board_mnt = leaders.Leaderboard()

cmd_parser = argparse.ArgumentParser()
cmd_parser.add_argument('mapfile', help='Mapfile name (`.map` is automatically added!)', type=str)
cmd_parser.add_argument('turns', help='No. of turns', type=int)
cmd_parser.add_argument('-b', dest='bots', help='participating bots', default=[], action='append')
cmd_args = cmd_parser.parse_args()

parser = ConfigParser()
parser.read("local_engine_settings.ini")
engine_options = {	"turntime"    : float,
					"loadtime"    : float,
					"epochs"      : int,
					"threshold"   : int,
					"map_dir"     : str,
					"log_dir"     : str,
					"json_logdir" : str,
					"cellar"      : str,
					"arena"       : str,
					"base_dir"    : os.getcwd(),
					"game_id"     : None,
					"turns"       : cmd_args.turns}
for option in parser.options('Engine'):
		engine_options[option] = engine_options[option](parser.get('Engine', option))
if len(cmd_args.bots) != 0:
	engine_options['json_logdir'] = "../game-ui/js"
game_options = {"turntime"    : engine_options["turntime"],
				"loadtime"    : engine_options["loadtime"],
				"turns"       : engine_options["turns"],
				"base_dir"    : os.getcwd(),
				"epochs"      : engine_options["epochs"],
				"threshold"   : engine_options["threshold"],
				"cspeed"      : float,
				"dcspeed"     : float,
				"max_arate"   : float,
				"regen"       : float,
				"amult"       : float,
				"amult_score" : float,
				"sc_pawn"     : float,
				"sc_loss"     : float,
				"bonus"       : int,
				"reward"      : int,}

for option in parser.options('Game'):
	game_options[option] = game_options[option](parser.get('Game', option))

mapfile = cmd_args.mapfile
map_dir = os.path.normpath(os.path.join( os.getcwd(), engine_options["map_dir"] ))
game_options["map"] = os.path.join(map_dir, mapfile+'.map')

json_replay_list = []
json_notifications = []
game = quantum.Game(game_options, json_replay_list, json_notifications)

if len(cmd_args.bots) == 0:
	# now we know how many bots are to be picked
	conn = pymysql.connect(host='localhost', user='ananya', passwd='ScherbiuS', db='bob')
	cur = conn.cursor()
	cur.execute("select * from teams;")
	res = cur.fetchall()
	all_teams = []
	for t in res:
		folder = os.path.join(engine_options['cellar'], t[1]+'_'+str(t[0]))
		fname = os.listdir(folder)[0]
		detail = {"name" : t[1],
				"id"    : t[0],
				"fname" : fname,
				"type"  : fname.split('.')[1]}
		if detail['type'] == 'py':
			detail['cmd'] = "python %s" % os.path.join(engine_options['arena'], fname)
		elif detail['type'] == 'prog':
			detail['cmd'] = "./%s" % os.path.join(engine_options['arena'], fname)
		else:
			raise RuntimeError("Invalid Bot Name %s @ %s" % (fname, folder))
		all_teams.append(detail)

	# generate all combinations (lazily)
	all_combinations = itertools.combinations(all_teams, game.bot_count)
else:
	combo = []
	for tfolder in cmd_args.bots:
		folder = os.path.join(engine_options['cellar'], tfolder)
		fname = os.listdir(folder)[0]
		tid = tfolder.split('_')[-1]
		tname = '_'.join(tfolder.split('_')[0:-1])
		detail = {"name" : tname,
				"id"    : int(tid),
				"fname" : fname,
				"type"  : fname.split('.')[1]}
		if detail['type'] == 'py':
			detail['cmd'] = "python %s" % os.path.join(engine_options['arena'], fname)
		elif detail['type'] == 'prog':
			detail['cmd'] = "%s" % os.path.join(engine_options['arena'], fname)
		else:
			raise RuntimeError("Invalid Bot Name %s @ %s" % (fname, folder))
		combo.append(detail)
	all_combinations = [combo]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MAIN LOOP ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("CWD", os.getcwd(), '\n')

for combo in all_combinations:
	json_replay_list = []
	json_notifications = []
	game = quantum.Game(game_options, json_replay_list, json_notifications)
	bot_details = [bd for bd in combo]
	# shuffle for important reason (hard-coding)
	random.shuffle(bot_details)
	if len(cmd_args.bots) == 0:
		# set game-id, generate a "URL" :P
		url = ''
		for bd in bot_details:
			url += '%d:' % (bd['id'])
		url += mapfile
		game_options["game_id"] = uuid.uuid3(uuid.NAMESPACE_URL, url)
		# check if this game has been run already!
		cur.execute("select count(*) from %s where game_id='%s'" % (mapfile, game_options['game_id']))
		if cur.fetchall()[0][0] == 1:
			print("SKIPPING as it ALREADY exists!\n%s\n" % game_options['game_id'])
			continue
	else:
		game_options["game_id"] = "_judge"

	# setup everything in arena/
	submit_folder = engine_options['cellar']
	for bot in bot_details:
		folder = os.path.join(submit_folder, bot['name']+'_'+str(bot['id']))
		if bot['type'] == 'py':
			shutil.copy2(os.path.join(folder, bot['fname']), engine_options['arena'])
			shutil.copy2('util.py', engine_options['arena'])
			shutil.copy2('Quantum.py', engine_options['arena'])
		elif bot['type'] == 'prog':
			shutil.copy2(os.path.join(folder, bot['fname']), engine_options['arena'])

	if SHOW_ASSIGNMENT:
		if DEBUG:
			print("-"*80)
			print("# of bots in Map '%s' is %d" % (mapfile, game.bot_count))
		for i, bot in enumerate(bot_details):
			print("bot%2d is %s(%d)" % (i, bot['name'], bot['id']))
	if DEBUG:
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

	result, json_start, json_end, json_ipstreams, json_invalid, json_ignored, json_valid = engine.run_game(game, bot_details, engine_options)
	# json_replay_list is also ready,
	# jsonize it
	json_replay = json.dumps(json_replay_list, separators=(',', ':'))
	jnotify     = json.dumps(json_notifications, separators=(',', ':'))
	# do more logging
	if os.path.exists(engine_options["json_logdir"]):
		json_data_dump = open( os.path.join( engine_options["json_logdir"], "game_replay%s.js" % game_options['game_id']), 'w' )
		# Legend
		json_data_dump.write("LEGEND=%s;\n" % json.dumps(bot_details, separators=(',', ':')))
		# start and replay are common to all
		json_data_dump.write("GAME_START=%s;\nGAME_REPLAY=%s;\n" % (json_start, json_replay))
		# *streams are not same. Hence *STREAMS is a list of *streams.
		json_data_dump.write("IP_STREAMS=%s;\nINV_STREAMS=%s;\nIGN_STREAMS=%s;\nVAL_STREAMS=%s;\n" % (json_ipstreams, json_invalid, json_ignored, json_valid))
		# notifications have "bot_id" embedded.
		json_data_dump.write("GAME_END=%s;\nGAME_NOTIFICATIONS=%s;\n" % (json_end, jnotify))
		json_data_dump.close()

	if DEBUG:
		print()
		for k in result.keys():
			print(k, ':', result[k])
	if SHOW_RESULT:
		print("\n\n"+str(game_options["game_id"]))
		print("scores :\t", result['score'])
		print("status :\t", result['status'])
		print("pturns :\t", result['player_turns'])
	# update ELO ratings!!
	[print(new_rating) for new_rating in board_mnt.do_rating([detail['id'] for detail in bot_details], result['score'], result['status'], result['player_turns'])]
	if len(cmd_args.bots) == 0:
		# save the replay in DB
		insq = "insert into %s values ( '%s'" % (mapfile, str(game_options["game_id"]))
		for detail in bot_details:
			insq += ", '%d'" % detail['id']
		insq += ");"
		insert_safely(cur, insq)

	# close FDs!
	engine_options["game_log"].close()

	if DEBUG:
		print("\nDONE\n" + "="*4)
		print("You can see the logs in `../logs` and game_replay in `../replays/game_replay%s.js`!\nCleaning `arena/` ..." % game_options['game_id'])
	
	this_dir = os.getcwd()
	os.chdir('arena')
	l = os.listdir()
	for i in l:
		try:
			os.remove(i)
		except:
			shutil.rmtree(i)
	os.chdir(this_dir)

if len(cmd_args.bots) == 0:
	conn.commit()
	board_mnt.commit('teams')
	# show how many in this table
	cur.execute("select count(*) from %s;" % mapfile)
	print("\nNow %s table has: %d" % (mapfile, cur.fetchall()[0][0]))
	cur.close()
	conn.close()