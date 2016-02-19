import os, sys, pymysql, shutil, subprocess

DEBUG = False
#import play_local

header = '''#ifndef __%s__
#define __%s__

#include "Quantum.h"

class myBot{
	string name;
public:
	myBot();
	myBot(string _name);
	void do_setup(ServerStack &game);
	void do_turn(ServerStack &game);
	void end_game(ServerStack &game);
};

#endif'''

launcher = '''#include "%s"
#include "Quantum.h"
#include <string>
#include <iostream>

using namespace std;

inline string rstrip(string &s, string remove_chars="\\n\\r"){
	size_t found = s.find_last_not_of(remove_chars);
	if (found != string::npos)
		s.erase(found+1);
	else
		s.clear(); 
	return s;
}

void launch(myBot bot){
	ServerStack game_state;
	string map_data = "";
	string cline;
	const string strip_chars = "\\n\\r";

	while(game_state.active){
		getline(cin, cline);
		cline = rstrip(cline, strip_chars);
		if(cline == ""){
			continue;
		}else if(cline == "ready"){
			game_state.setup(map_data);
			bot.do_setup(game_state);
			cout<<"go\\n";
			cout.flush();
			map_data = "";
		}else if(cline == "go"){
			game_state.update_state(map_data);
			if(game_state.active){
				bot.do_turn(game_state);
			}
			cout<<"go\\n";
			cout.flush();
			map_data = "";
		}else{
			map_data += cline + "\\n";
		}
	}
	// game is over (or I got kicked out!)
	bot.end_game(game_state);
}

int main(){
	// Give your BOT a cool name!
	launch(myBot("%s"));
	return 0;
}'''

makefile='''DEPS = util.h Quantum.h bot_template.h
HC = util.o Quantum.o %s.o %s_launcher.o

%%.o: %%.cpp $(DEPS)
	g++ -c -o $@ $< -Wall -std=c++14 -lm

%s_launcher.prog: $(HC)
	g++ -std=c++14 -Wall -o $@ $^
'''

def insert_safely(cursor, myquery):
	try:
		cursor.execute(myquery)
		return True and DEBUG
	except (pymysql.err.IntegrityError, pymysql.err.ProgrammingError) as e:
		if DEBUG:
			print("-<|WARNING|>- Skipped an insert as %s"%e)
		return False

def get_list():
	team_list = [team for team in os.listdir('submits') if os.path.isdir(os.path.join('submits', team))]
	teams = []
	for item in team_list:
		tid = item.split('_') [-1]
		tname = '_'.join(item.split('_') [:-1])
		teams.append((int(tid), tname))
	return teams

def view_db(cur, table=None):
	if table != None:
		cur.execute('select * from %s;' % table)
		relations = cur.fetchall()
	else:
		cur.execute('show tables;')
		relations = cur.fetchall()
	res = ""
	for item in relations:
		res += str(item)+'\n'
	return res

def prepare(teams):
	for team in teams:
		folder = os.path.join('submits', team[1]+'_'+str(team[0]))
		fnames = os.listdir(folder)
		exts = []
		for fname in fnames:
			try:
				exts.append(fname.split('.')[1])
			except IndexError:
				pass
		if 'cpp' in exts:
			print("Preparing cpp bot of %s(%d)" % (team[1], team[0]))
			# find that cpp file, check if it includes "bot_template.h"
			cpp_file_name = fnames[exts.index('cpp')]
			cpp_file_name_base = cpp_file_name.split('.')[0]
			with open(os.path.join(folder, cpp_file_name), 'r') as cpp_file:
				file_contents = cpp_file.read(200)
				if file_contents.find('bot_template.h') < 0:
					print("Please checkout team:%d.%s (cpp) header failed!" % (team[0], team[1]))
					break

			print("\tCopying files...")
			shutil.copy2('../bin/Quantum.o', folder)
			shutil.copy2('../bin/util.o', folder)
			shutil.copy2('../bin/Quantum.h', folder)
			shutil.copy2('../bin/util.h', folder)
			
			print("\tMaking Headers, Makefile...")
			header_file = open(os.path.join(folder, 'bot_template.h'), 'w')
			header_file.write(header % ('USR_'+team[1].upper(), 'USR_'+team[1].upper()))
			header_file.close()
			
			launcher_file = open(os.path.join(folder, team[1]+'_launcher.cpp'), 'w')
			launcher_file.write(launcher % ('bot_template.h', team[1]))
			launcher_file.close()

			makefile_file = open(os.path.join(folder, 'Makefile'), 'w')
			makefile_file.write(makefile % (cpp_file_name_base, team[1], team[1]))
			makefile_file.close()

			print("\tCompiling..")
			ret_state = subprocess.run("cd submits/%s/;make %s_launcher.prog" % (team[1]+'_'+str(team[0]), team[1]), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			if (ret_state.returncode != 0):
				print("STDOUT\n======\n"+ret_state.stdout.decode('utf8'))
				print("STDERR\n======\n"+ret_state.stderr.decode('utf8'))
			else:
				print("\tCleaning dir...")
				for fname in fnames:
					if fname == "%s_launcher.prog" % team[1]:
						pass
					else:
						os.remove(os.path.join(folder, fname))
				print("%s(%d) is now ready." % (team[1], team[0]))
		#print (fnames)

if __name__ == '__main__':
	# register all teams
	
	conn = pymysql.connect(host='localhost', user='ananya', passwd='ScherbiuS', db='bob')
	cur = conn.cursor()
	team_list = get_list()
	for tid, tname in  team_list:
		insert_safely(cur, "insert into teams(team_id, name) values(%d, '%s');" %(tid, tname))
	conn.commit()
	print(view_db(cur, 'teams'))
	
	# prepare all bots
	prepare(get_list())
	
	# close db
	cur.close()
	conn.close()