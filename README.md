Please see [Contribution Guidlines](Contributing.md)
====================================================

Saber
=====

These topics are broadly what we need to worry about. Game has been decided.
**Quantum-tentacle-wars**
> *But we still need a name!*

   :star: Rule specification needs to be ready.
<br>:star: Please fill in the parts of README which are your responsibility or you have knowledge about.
<br>:star: Use Sublime Text for editing this `md` document

Sandboxing and Communication
----------------------------

I've been reading the Google ANTS challenge source code. Their engine runs on `python`.
`playgame.py` plays several rounds of the Game with the same bots to get GameResults by calling `engine.run_game` for each round.
`run_game` opens log-files and istantiates all *bots*.
Each *bot* is actually a `Jail` object, *aka. sandbox*.
> I guess we will not be able to setup secure environment on pythonanywhere, so we'll have to preprocess the source file and deem whether it is safe or not.

:question: How to determine security flaws in source (`c++`, `c`, `py`) code?

###Sandboxes
> Secure execution of bots, but **requires** setting up of `chroot` etc on the linux machine.

Upon `init`, a Jail tries to acquire a *jail* from a *jail-pool* residing in the `chroot` (protected) directory.
It declares 3 queues: `response`, `stdout`, `stderr` and the `_prepares()` the Jail by copying the all the files related to this bot into the `chroot/jailXX/scratch/home/<bot-name>`. Then a weird command is run: `("sudo mount chroot/jailXX/root")`
Then `jail_own.c` is called to change ownership of this jail to something else, *god knows what!*

It's time to start the bot now, by calling `start("bot_wd")`. `self.chroot_cmd + bot_wd` is run inside a `SubProcess` object with named pipes. A daemon thread is invoked that executes `_guard_monitor()`, which is an infinite loop that monitors and processes the `subprocess.stdout` to dump everything into the respective queues. It puts the `stdout` lines into the correct queues *(which belong to the Jail object)*.
The jail object provides methods:

* to directly write to stdin of the bot
* to read the `stdout` and `stderr` queues which hold the o/p of the bot
* to send signals like `stop`, `cont`, `kill`

###Houses
> Insecure execution of bots, requires no special system setup.

This is not a Jail object.
It does not copy the *bot*-directory anywhere, just executes from it.
Determines the path-to-*bot* and invokes a SubProcess to run it (normal execution : `./<bot-name>`) with 3 queues `stdin`, `stdout`, `stderr`.
2 daemon threads are invoked to execute `_monitor()`, which is an infinte loop that monitors and processes `subprocess.stdout` or `stderr`.
Another thread targets `_child_writer()` which uses self.child_queue and dumps whatever it finds there into `subprocess.stdin`.
The jail object provides methods:

* to directly write to stdin of the bot
* to read the `stdout` and `stderr` queues which hold the o/p of the bot
* to send signals like `stop`, `cont`, `kill`

Game Engine and Resource Manager
--------------------------------

Invokes a round that procures resources from a pool. If a simple count of **threads-in-use** and **total-mem-used** is enough to avoid exceeding resource use (this can happen at peak time when $N$ users need to run their game).

Sample Bots
-----------

Map Creation
------------

Leaderboards
------------

ELO rating system: [*wiki*](https://en.wikipedia.org/wiki/Elo_rating_system), [*epic blog on rating systems*](http://www.moserware.com/2010/03/computing-your-skill.html)

Automated Rounds
----------------

Website (frontend)
------------------

###Javascript game

###Management

Registration, submissions, user tracking