#include "donothing.h"

//You can define your functions here.

void all_dumps(ServerStack &game){
	game.pretty_dump_alerts();
	game.pretty_dump_additions();
	game.pretty_dump_deletions();
}

// <your function>

void myBot::do_setup(ServerStack &game){
	return;
}

void myBot::do_turn(ServerStack &game){
	return;
}

void myBot::end_game(ServerStack &game){
	// call the functions you defined above, over here.
	game.error_dump("Bye Folks!");
	return;
}

//DON'T EDIT below this
myBot::myBot() {}

myBot::myBot(string _name){	
	name = _name;
}
