"""
A file for the attributes of the world (IE, the physical things the
 robot cares about, including its own body).
 These will be fixed for a given
run of the program, but we may want to tweak them.  I include them in
a class (basically a structure) so that the notation will be suggestive
of the reference to this file.
"""
import sys
sys.path.append( "robot" )
from robotbasics import *
from settings import *


class World:
    import localize
    treeSide = 3.5 / 12 #a tree is 3.5 inches on each side
    rockRadius = 6.7/12/2 #a paint can has a 6.7 inch diameter
    logList = []
    landmarkList=[  Landmark(3.0,3.0,"ROCK"),
                    Landmark(5.0,3.0, "TREE"),
                    Landmark(3.0,5.0, "TREE"),
                    ]
    wheelOffset=(.5,.5) #the x and y offsets of the wheels' stems from the center of the bot
    wheelDims=(2/12, 3/12)
    eyeList=(localize.Eye( 0 ,0.415,-0.415,  90.0, SCAN_DATA_POINTS, SCAN_ANGLE),
            localize.Eye(  1 ,-0.415,-0.415,  225.0, SCAN_DATA_POINTS, SCAN_ANGLE),
            localize.Eye(  2 ,-0.415,0.415,  270.0, SCAN_DATA_POINTS, SCAN_ANGLE),
            localize.Eye(  3 ,0.415,0.415,  45, SCAN_DATA_POINTS, SCAN_ANGLE))
    robotSide = 1.0
