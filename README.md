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
<br>:star: The [wiki](wiki) is up and running. Any long explanations must end up there.

Sandboxing and Communication
----------------------------

I've been reading the Google ANTS challenge source code. Their engine runs on `python`.
`playgame.py` plays several rounds of the Game with the same bots to get GameResults by calling `engine.run_game` for each round.
`run_game` opens log-files and istantiates all *bots*.
Each *bot* is actually a `Jail` object, *aka. sandbox*.
> I guess we will not be able to setup secure environment on pythonanywhere, so we'll have to preprocess the source file and deem whether it is safe or not.

:question: How to determine security flaws in source (`c++`, `c`, `py`) code?

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