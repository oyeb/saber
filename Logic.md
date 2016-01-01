Engine Architecture
===================

`play_game.py` accepts command-line arguments, bots, game-options, engine-options, etc and invokes *"rounds"*.

* In each round, a `quantum.Game` object is created which basically handles the the whole shared game state.
* Then, `engine.run_game()` is called which, does most of the work:

	* Opens all the log files (bot-level *(and possibly, game-level)*)
	* Starts the sandboxes via `house.get_sandbox()` for each bot
	* Sends initial game state via the `Game` object and waits for `ready` from each bot *(with, of course, a timeout)*
	* Each *turn* consists of a single *move* from each bot.
		* Sends *updated views* of the *game-state* to each bot just before their *move*.
		* Waits for a *move* to be returned.
		* Updates the *game-state* immediately via the methods of the `Game` object.
		* A score is awarded to each bot after each *turn*.
		* Eliminates dead bots and performs other logging stuff
	* Ends game.

* Control comes back to `play_game` which conducts another rounds by changing the positions of the bots in the map.
* Leaderboard rating is generated.

The game is run *serially*. This has major drawbacks. This system can handle parallel execution but, will it make sense? That depends on the `Game Specification and Rules`. **Need to work them out before Jan 6**.

Sandbox Operation
-----------------

Is described partially in the [readme](README.md).

* Basically, this opens a `Subprocess` that invokes `python /path-to-bot/botX.py` with named pipes for the `std` files.
* It instantiates 3 queues, one for each.
* It launches 2 threads that dump any data that arrives on `stderr` and `stdout` into a `Queue` or a log-file.
* The thread that is most interesting is the one that reads the `in_queue` continuously and dumps any arriving data onto `SubProcess.stdin`, which is utilised by the bot as a *turn* input.
* the `sandbox` objects provides methods that can suspend, kill, resume the `Subprocess`.

What will our users get?
------------------------

They will get a `bot-template` file, and `Quantum.py`. Look at the last line in each `botX.py` file, `__main()__` invokes the `Quantum.ServerStack.run()` method.

This creates a `ServerStack` object that parses the `stdin` for the user automatically into the correct data containers, which are accessible to `myBot` class. It's a pretty sweet setup. User only edits the `do_setup` and `do_turn` methods which are called by the `ServerStack` object whenever it recieves data from the *Game Engine* **(quantum.Game.get_player_view())**.

In case of `cpp`, we will have to write `quantum.Game` in `cpp`. That's a daunting task.