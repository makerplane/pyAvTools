===========================================
MakerPlane Aviation Module Tool Kit
===========================================

Copyright (c) 2019 MakerPlane

pyAvTools is an open source aviation tool kit, providing useful modules for Python based
Aviation apps, including:
    * Data management package for charting objects
    * Flight Information eXchange (FIX) database module
    * A hard-button based user interface layer utilizing Qt (no keyboard or mouse required)
        * Uses a rotary encoder + push buttons
        * NumberWidget (Show/Change a number)
        * ChoiceWidget (Show/Change a radio-button style section)
        * SelectMenuWidget (Show/Change a menu style section)
        * FIXDisplay (Show a collection of FIX database items)
    * Others for future consideration

Installation
------------

Begin by cloning the Git repository

::

    git clone git@github.com:makerplane/pyAvTools.git

or

::

    git clone https://github.com/makerplane/pyAvTools.git 


If you'd like to install the program permanently to your system or into a virtualenv you
can issue the command...

::

  sudo pip3 install .

from the root directory of the source repository.  **Caution** This feature is still
in development and may not work consistently.

Development
-----------

To set up your development environment, you can create a virtualenv:

::

  make venv

Then, you can install all required dependencies:

::

  make init

Afterwards, you are ready to develop. Once one or more dependencies have changed, simply run
`make init` again.

Requirements
------------
