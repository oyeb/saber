/*
 *	DON'T EDIT THIS FILE!
 *	._____________________________________________________________.
 *	|Edit special.cpp instead. That's where SPECIAL BOT resides.  |
 *	'-------------------------------------------------------------'
 *	
 *	This file is just used to launch your BOT.
 *
*/

#include "special.h"
#include "Quantum.h"
#include <string>
#include <iostream>

using namespace std;

inline string rstrip(string &s, string remove_chars="\n\r"){
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
	const string strip_chars = "\n\r";

	while(game_state.active){
		getline(cin, cline);
		cline = rstrip(cline, strip_chars);
		if(cline == ""){
			continue;
		}else if(cline == "ready"){
			game_state.setup(map_data);
			bot.do_setup(game_state);
			cout<<"go\n";
			cout.flush();
			map_data = "";
		}else if(cline == "go"){
			game_state.update_state(map_data);
			if(game_state.active){
				bot.do_turn(game_state);
			}
			cout<<"go\n";
			cout.flush();
			map_data = "";
		}else{
			map_data += cline + "\n";
		}
	}
	// game is over (or I got kicked out!)
	bot.end_game(game_state);
}

int main(){
	// Give your BOT a cool name!
	launch(myBot("special"));
	return 0;
}