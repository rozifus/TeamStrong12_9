Moon Patrol
===========

Entry in PyWeek #15  <http://www.pyweek.org/15/>
URL: yourgameurl
Team: team-strong-
Members: rozifus,jtrain
License: see LICENSE.txt

Credit for assets used
----------------------

pink-summertime.mod - chiptune accessed from http://www.chiptune.com/



Installing the Game (dev env)
-------------------

virtualenv
==========

# creates an empty virtual environment
virtualenv .

# activates the virtual environment
source bin/activate

clone game
==========

git clone git@github.com:rozifus/TeamStrong12_9.git tstrong

install reqs
============

# one the game zip file unzipped (or git cloned) to tstrong:
pip install -r tstrong/requirements.txt

run game
========

cd tstrong
python run_game.py

Running the Game
----------------

On Windows or Mac OS X, locate the "run_game.pyw" file and double-click it.

Othewise open a terminal / console and "cd" to the game directory and run:

  python run_game.py


How to Play the Game
--------------------

Constantly moving left. Dodging enemies and obstacles. Shooting with space bar.

Development notes 
-----------------

Creating a source distribution with::

   python setup.py sdist

You may also generate Windows executables and OS X applications::

   python setup.py py2exe
   python setup.py py2app

Upload files to PyWeek with::

   python pyweek_upload.py

Upload to the Python Package Index with::

   python setup.py register
   python setup.py sdist upload

