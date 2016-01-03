Usage
=====

You can find out more information about the bots in the [wiki](wiki).

* `bot[12].py` have been removed.

fake_engine is ready!
---------------------

`bot[34].py` are invoked inside the whole system. Just invoke `bash ./launch.sh`. This will:

* Invokes `play_game.py` with the right command-line args and `bot3.py` and `bot4.py`.
* `play_game.py` will call `run_game()`, which is the heart of the operation.

You can find the logs of the game in [`arena/logs`](arena/logs). To know more about the *fake-game* read [this](wiki/Bots-and-Game-Specs)