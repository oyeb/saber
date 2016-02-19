/*
	DON'T EDIT THIS FILE, edit bot_template.cpp instead!
*/
#ifndef __BOT_TEMPLATE__
#define __BOT_TEMPLATE__

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

#endif