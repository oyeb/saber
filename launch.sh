#!/usr/bin/bash
turntime=2
loadtime=2
turns=30
points=1
_map="maps/test.map"
python3 saber/play_game.py -m  $_map\
					-t  $turns\
					-tt $turntime\
					-ld $loadtime\
					--points $points\
					-b "bots/bot6.py"\
					   "bots/bot5.py"\
					-l ../saber_backend/media/logs\
					-a ../saber_backend/media/arena\
					-cs 5\
					-dcs 10\
					--amult 3.2\
					-rg 0.8\
					-ar 5.0