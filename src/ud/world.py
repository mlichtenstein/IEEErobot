"""
A file for the attributes of the world (IE, the physical things the
 robot cares about, including its own body).
 These will be fixed for a given
run of the program, but we may want to tweak them.  I include them in
a class (basically a structure) so that the notation will be suggestive
of the reference to this file.
"""

from robotbasics import *
from settings import *

class World:
    import localize
    treeSide = 3.5 / 12 #a tree is 3.5 inches on each side
    rockRadius = 6.7/12/2 #a paint can has a 6.7 inch diameter
    logList = [(0.00,4.00,3.00,0.00),
                (3.07,0.16,4.00,4.04),
                (7.54,0.00,5.00,1.49),
                (7.54,3.00,5.00,5.85),
                (7.96,5.60,4.00,1.92),
                (0.02,6.00,6.02,7.96),
                (3.33,7.96,2.17,4.30)]
    landmarkList=[Landmark(1.50,7.29,"ROCK"),
                    Landmark(1.96,5.06, "TREE"),
                    Landmark(2.15,2.08, "TREE"),
                    Landmark(4.15,0.98, "ROCK"),
                    Landmark(3.91,4.98, "ROCK"),
                    Landmark(6.14,6.16, "TREE"),
                    Landmark(7.85,1.65, "TREE")]
    wheelOffset=(.5,.5) #the x and y offsets of the wheels' stems from the center of the bot
    wheelDims=(2/12, 3/12)
    eyeList=(localize.Eye(0,  0.415,-0.415,  90.0, SCAN_DATA_POINTS, SCAN_ANGLE),
            localize.Eye(1,  -0.415,-0.415,  90.0, SCAN_DATA_POINTS, SCAN_ANGLE),
            localize.Eye(2,  -0.415,0.415,  90.0, SCAN_DATA_POINTS, SCAN_ANGLE),
            localize.Eye(3,  0.415,0.415,  90.0, SCAN_DATA_POINTS, SCAN_ANGLE))
