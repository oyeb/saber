#!/usr/bin/env python

import time
import datetime
import traceback
import os
import random
import sys
import json
import copy

import house

MAX_BOT_MOVES   = 4000
MAX_ERROR_LINES = 1000

if sys.version_info >= (3,):
	def unicode(s, errors="strict"):
		if isinstance(s, str):
			return s
		elif isinstance(s, bytes) or isinstance(s, bytearray):
			return s.decode("utf-8", errors)
		raise SandboxError("Tried to convert unrecognized type to unicode")

def run_game(game, bot_details, options):
	# instantiate logs
	bot_count = len(bot_details)
	input_logs  = [open(os.path.join(options["log_dir"], "bot%d.input.log" % i), 'w') for i in range(bot_count)]
	output_logs = [open(os.path.join(options["log_dir"], "bot%d.output.log" % i), 'w') for i in range(bot_count)]
	error_logs  = [open(os.path.join(options["log_dir"], "bot%d.error.log" % i), 'w') for i in range(bot_count)]

	json_mybot_ipstream = []
	json_mybot_invalid  = []
	json_mybot_valid    = []
	json_mybot_ignored  = []

	# prepare list of bots (houses)
	bots = []
	b_turns = []
	bot_status = ['survived' for i in range(bot_count)]
	turn = 0
	try:
		for bid, detail in enumerate(bot_details):
			s = house.get_sandbox(options["arena"])
			s.start(detail['cmd'])
			bots.append(s)
			b_turns.append(0)
			# make sure the houses are all functioning
			if not s.is_alive:
				bot_status[bid] = "crashed @ 0, did not start."
				game.kill_player(bid)
			s.pause()

		cspoke_id = 0
		spokes = [' | ', ' / ', '---', ' \ ']
		sys.stdout.write("turn         ")
		sys.stdout.flush()
		for turn in range(options["turns"]+1):
			#turn ____ ___
			if turn%5 == 0:
				if turn%10 == 0:
					sys.stdout.write('\b'*8+"%4d %s"%(turn, spokes[cspoke_id]))
				else:
					sys.stdout.write('\b'*3+"%s" % (spokes[cspoke_id]))
				cspoke_id = (cspoke_id+1)%4
				sys.stdout.flush()

			if turn == 0:
				game.start_game()
				options["game_log"].write(game.get_start_player())
				# create the start json data
				json_start = game.get_start_json()
			for bid, bot in enumerate(bots):
				if game.is_alive(bid):
					if turn == 0:
						# send game state to all
						start_msg = game.get_start_player(bid)+'ready\n'
						bot.write(start_msg)
						input_logs[bid].write(start_msg)
					else:
						# send updates to all
						update = 'turn~%d\n%sgo\n' % (turn, game.get_player_update(bid))
						bot.write(update)
						input_logs[bid].write(update)
						b_turns[bid] = turn
						json_mybot_ipstream.append(update)
					input_logs[bid].flush()
			
			if turn > 0:
				game.start_turn()
				options["game_log"].write( "turn~%d\n%s\n" % (turn, game.get_current_state()) )
				options["game_log"].flush()

			# get moves from all. Wait till timeout. Bots run in parallel.
			time_limit = options["loadtime"] if (turn == 0) else options["turntime"]
			
			alive_bot_list = [(bid, bot) for (bid, bot) in enumerate(bots) if game.is_alive(bid)]
			moves, errors, statuses = get_moves(game, alive_bot_list, bot_status, time_limit, turn, options["game_log"])
			# moves is a dict of lists. Each list is the list of lines read from stdout

			# process errors
			for bid in errors.keys():
				if errors[bid]:
					error_logs[bid].write(unicode('\n').join(errors[bid])+unicode('\n'))
			for bid in statuses.keys():
				# this copying is required since bot_status has statuses of all bots but the dict only has info about a few
				bot_status[bid] = statuses[bid]
			# list of currently alive bots. After this turn, some might die!
			currently_active_bots = [b for b in range(bot_count) if game.is_alive(b)]
			
			# process moves (game.parse_move)
			if turn > 0 and not game.over():
				# alive_bot_list bots may have been killed in get_moves()
				for bid, bot in alive_bot_list:
					if game.is_alive(bid):
						valid, invalid, ignored = game.do_move(bid, moves[bid])
						# log everything
						output_logs[bid].write('# turn %s\n' % turn)
						if valid:
							output_logs[bid].write('\n'.join(valid)+'\n')
							json_mybot_valid.append({"turn"  : turn,
													"moves" : valid[:]})
						if ignored:
							json_mybot_ignored.append({"turn"  : turn,
													"moves" : ignored[:]})
							error_logs[bid].write('turn %4d bot %s ignored actions:\n' % (turn, bid))
							error_logs[bid].write('\n'.join(ignored)+'\n')
							error_logs[bid].flush()

							output_logs[bid].write('\n'.join(ignored)+'\n')
						if invalid:
							json_mybot_invalid.append({"turn"  : turn,
													"moves" : invalid[:]})
							error_logs[bid].write('turn %4d bot %s invalid actions:\n' % (turn, bid))
							error_logs[bid].write('\n'.join(invalid)+'\n')
							error_logs[bid].flush()

							output_logs[bid].write('\n'.join(invalid)+'\n')
						output_logs[bid].flush()

			if turn > 0:
				game.finish_turn()
			
			# find bots that were eliminated in this turn
			eliminated = [b for b in currently_active_bots if not game.is_alive(b)]
			for bid in eliminated:
				if bot_status[bid] == "survived":
					bot_status[bid] = "eliminated"
				options["game_log"].write("Poor bot%d has been pawned!" % bid)
				options["game_log"].flush()
				scores = "scores %s\nmy_score %d\n" % (' '.join(map(str, game.get_scores())), game.get_scores(bid))
				status = "status %s\n" % ' '.join(bot_status)
				finale = "end\n" + scores + status + "go\n"
				bots[bid].write( finale )
				input_logs[bid].write(finale)
				input_logs[bid].flush()
			
			# did game end before max_turns?
			if game.over():
				break
		# end game
		game.finish_game()
		scores = ' '.join(map(str, game.get_scores()))
		status = ' '.join(map(str, bot_status))
		options["game_log"].write( "%s\nscores %s\nstatus %s\nGAME-OVER\n" % ("*" * 15, scores, status) )
		options["game_log"].flush()
		# json end game
		json_end = json.dumps({'scores' : game.get_scores()}, separators=(',', ':'))								
		
		for bid, bot in enumerate(bots):
			if game.is_alive(bid):
				scores = "scores %s\nmy_score  %d\n" % ( ' '.join(map(str, game.get_scores())), game.get_scores(bid) )
				status = "status %s\nmy_status %s\n" % ( ' '.join(map(str, bot_status)), bot_status[bid] )
				finale = "end\n" + scores + status + "go\n"
				input_logs[bid].write(finale)
				input_logs[bid].flush()
				bot.write(finale)
	
	except Exception as e:
		error = traceback.format_exc()
		print("\nException Occured\n", e)
		print("\nTraceback Object\n", error)

	finally:
		# kill all bots, release sandboxes
		for bot in bots:
			if bot.is_alive:
				bot.kill()
			bot.release()
	# awesome shit!
	sys.stdout.write('\b'*3)
	sys.stdout.write('Done!')
	sys.stdout.flush()
	# consolidate game result
	game_result = {	"game_id"      : options["game_id"],
					"time"         : str(datetime.datetime.now()),
					"status"       : bot_status,
					"player_turns" : b_turns,
					"score"        : game.get_scores(),
					"game_length"  : turn}
	json_ipstream = json.dumps(json_mybot_ipstream, separators=(',', ':'))
	json_invalid  = json.dumps(json_mybot_invalid, separators=(',', ':'))
	json_ignored  = json.dumps(json_mybot_ignored , separators=(',', ':'))
	json_valid    = json.dumps(json_mybot_valid , separators=(',', ':'))

	# close all file descriptors!
	for f in input_logs:
			f.close()
	for f in output_logs:
		f.close()
	for f in error_logs:
		f.close()

	# done
	return game_result, json_start, json_end, json_ipstream, json_invalid, json_ignored, json_valid
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#

def get_moves(game, bots, old_status, time_limit, turn, global_game_log):
	bot_finished = {b:False for b, _ in bots}
	bot_moves = {b:[] for b, _ in bots}
	error_lines = {b:[] for b, _ in bots}
	statuses = {b:ostat for b, ostat in enumerate(old_status)}

	# resume all bots
	for bid, bot in bots:
		if bot.is_alive:
			bot.resume()

	# don't start timing until the bots are started
	start_time = time.time()
	# print("GM:", start_time, "for", time_limit)
	
	# loop until received all bots send moves or are dead
	#   or when time is up
	while (sum(bot_finished.values()) < len(bot_finished) and
			time.time() - start_time < time_limit):
		time.sleep(0.01)
		for b, bot in bots:
			if bot_finished[b]:
				continue # already got bot moves
			if not bot.is_alive:
				error_lines[b].append(unicode('bot%d crashed @ turn %4d\n') % (b, turn))
				statuses[b] = 'crashed'
				global_game_log.write(unicode('bot%d crashed @ turn %4d\n') % (b, turn))
				global_game_log.flush()
				line = bot.read_error()
				while line != None:
					error_lines[b].append(line)
					line = bot.read_error()
				bot_finished[b] = True
				game.kill_player(b)
				continue # bot is dead

			# read a maximum of 100 lines per iteration
			for x in range(100):
				line = bot.read_line()
				if line is None:
					# stil waiting for more data
					break
				line = line.strip()
				if line.lower() == 'go':
					bot_finished[b] = True
					# bot finished sending data for this turn
					break
				bot_moves[b].append(line)

			for x in range(100):
				line = bot.read_error()
				if line is None:
					break
				error_lines[b].append(line)
	# pause all bots again
	for bid, bot in bots:
		if bot.is_alive:
			bot.pause()

	# check for any final output from bots
	for b, bot in bots:
		if bot_finished[b]:
			continue # already got bot moves
		if not bot.is_alive:
			error_lines[b].append(unicode('bot%d crashed @ turn %4d\n') % (b, turn))
			statuses[b] = 'crashed'
			global_game_log.write(unicode('bot%d crashed @ turn %4d\n') % (b, turn))
			global_game_log.flush()
			line = bot.read_error()
			while line != None:
				error_lines[b].append(line)
				line = bot.read_error()
			bot_finished[b] = True
			game.kill_player(b)
			continue # bot is dead

		line = bot.read_line()
		while line is not None and len(bot_moves[b]) < MAX_BOT_MOVES:
			line = line.strip()
			if line.lower() == 'go':
				bot_finished[b] = True
				# bot finished sending data for this turn
				break
			bot_moves[b].append(line)
			line = bot.read_line()

		line = bot.read_error()
		while line is not None and len(error_lines[b]) < MAX_ERROR_LINES:
			error_lines[b].append(line)
			line = bot.read_error()

	# kill timed out bots
	for b in bot_finished.keys():
		if not bot_finished[b]:
			error_lines[b].append(unicode('Slow bot%d timed out @ turn %4d\n') % (b, turn))
			statuses[b] = 'timeout'
			global_game_log.write(unicode('Slow bot%d timed out @ turn %4d\n') % (b, turn))
			global_game_log.flush()
			# find 'b' in bots
			# assign to dead_bot
			for bb, bot in bots:
				if bb == b:
					dead_bot = bot
			for x in range(100):
				line = dead_bot.read_error()
				if line is None:
					break
				error_lines[b].append(line)
			game.kill_player(b)
			dead_bot.kill()
	# remember that these are dicts!!
	# bot_moves[bid] is a list of lines, unstripped
	return bot_moves, error_lines, statuses
