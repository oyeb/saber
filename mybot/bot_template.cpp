/*Make sure you include "bot_template.h"

This file must have definitions for:
====================================
	* myBot::myBot()
	* myBot::myBot(string)
	* myBot::do_setup(ServerStack&)
	* myBot::do_turn(ServerStack&)
	* myBot::end_game(ServerStack&)

You can define all your function here. Call them in
---------------------------------------------------
	* do_setup()
	* do_turn()
	
Good Luck!
We request you to read the Walk-through and Manual before you satrt editing this file.

Read the Walkthrough              http://anokha.amrita.edu/bob/cpp/walkthru.html
Read the Manual                   http://anokha.amrita.edu/bob/cpp/manual.html
Read the C++ API                  http://anokha.amrita.edu/bob/cpp/api_cpp.html
Read the Game Specification       http://anokha.amrita.edu/bob/game-spec.html
*/
#include "bot_template.h"

//You can define your functions here.

void all_dumps(ServerStack &game){
	game.pretty_dump_alerts();
	game.pretty_dump_additions();
	game.pretty_dump_deletions();
}

// <your function>

void myBot::do_setup(ServerStack &game){
	// call the functions you defined above, over here.
	return;
}

void myBot::do_turn(ServerStack &game){
	if (game.turn == 4)
		game.attack(0, 3, 0.6);
	else if (game.turn == 23){
		game.withdraw(0, 3, 0.5);
		game.attack(3, 1, 0.8);
	}
	else if (game.turn == 70)
		game.withdraw(3, 1, 0.7);
	all_dumps(game);
	// call the functions you defined above, over here.
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
