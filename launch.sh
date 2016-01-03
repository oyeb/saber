#!/usr/bin/bash
turntime=2
loadtime=2
turns=10
points=1
_map="maps/small_map.map"
python3 play_game.py -m  $_map\
					-t  $turns\
					-tt $turntime\
					-ld $loadtime\
					--points $points\
					-b "bots/bot3.py"\
					   "bots/bot4.py"\
					-l arena/logs\
					-a arena