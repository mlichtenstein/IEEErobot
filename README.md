Hello Team Robot member!   Welcome to the repsoitory.  
IF you are a contributor, please keep all your changes in your own branch
unti one of the daily merge parties.  Woo!


What follows is a brief primer of the structure of
the code.

Directories:

    src/
        is the directory that contains code that will be run on the
        robot.  All other stuff (like this readme) should go below
        src.
    src/ud
        "Upper Deck" is the panda board.  The dir contains mostly python
        files, but also has a Makefile which will sychronize
        settings.h with settings.py
    src/ld
        "Lower Deck" is the arduino.  the dir has an .ino file and
        settings.h.  Unfortunately, because arduino IDE sucks, this
        is all we get, and everything has to go into one of those.

Upper Deck Files:
    main.py
        is the one you want to look at first.  It's the main loop.
        there's only one line that contains the action of the robot:
        robotMode = robotMode.act(state)
        it does the action associated with the current mode, then
        switches the mode to the next mode.
    modes.py
        contains all the action of the robot.  It consists of
        lots of modes which inheirit Mode's attributes (such
        as the serial connection).  Each mode has an act(state)
        method which contains what the robot does in that mode.
        Each act() method ends with the return of a different
        mode.  Look at it and see.
    robotbasics.py
        Contains the definitions of handy robot classes, mostly the definition
        of Pose, State, and Landmark.  If you think there's something else
        other people will want to call a lot, put it here.
    world.py
        definitions of the physical attributes of the robot + playing field
    messenger.py
        handles messenges to and from arduino
