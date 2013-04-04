"""
this library is for the basic building blocks of the representations
our robot uses.
"""

import sys
sys.path.append( "robot" )

class Pose:
    x=0
    y=0
    theta=0
    def __init__(self,x,y,theta):
        self.setPose(x,y,theta)
    def setPose (self,x,y,theta):
        self.x = x
        self.y = y
        self.theta = theta
    def randPose(self):
        import random
        self.x = random.random()*8
        self.y = random.random()*8
        self.theta = random.random()*360
    def string(self):
        #a method that returns a string that describes the bot.
        string = "x= {}' {:.1f}\"".format(int(self.x),(self.x-int(self.x))*12)\
                +", y= {}' {:.1f}\"".format(int(self.y),(self.y-int(self.y))*12)\
                +", theta= {:.1f}\"".format(self.theta)
        return string

class State:
    #The robot's internal state variables go here:
    def __init__(self):
        import time
        import localize
        import copy
        import world
        self.paused = False
        self.startTime = time.time()
        self.startPause = None
        self.mode = None
        self.moving = False
        self.pose = Pose(.5,.5,270) #make this the starting pose
        self.poseUncertainty = Pose(.3,.3,5) #total guesswork
        self.pitch = 0.0
        self.roll = 0.0
        self.distanceSinceScan = Pose(0,0,0) #distance, in feet, since last scan
        self.motorConfig = [0,0,0,0] #the thetas of each wheel servo
        self.motorPWM = 0, 0 #the duty cycle of the PWM output to each motor
        self.armConfig = [0,0,0] #the thetas of each arm servo
        self.hypobotCloud = localize.HypobotCloud()
        self.eyeList = copy.deepcopy(world.World().eyeList)
        self.remainingPucks = (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16)
        self.magnetOn = False
        self.lightsOn = False
    def pause(self):
        import time
        self.startPause = time.time()
    def unpause(self):
        if self.startPause == None:
            #this doesn't nec need to be an exception
            raise Exception("Unpaused robot without pausing!  Oh noes!")
        else:
            import time
            pauseDuration = time.time()-self.startPause
            self.startTime += pauseDuration
            self.startPause = None
        

class Landmark:
    def __init__(self, x, y, landmarkType):
        if landmarkType != "TREE" and landmarkType!= "ROCK":
            raise Exception("landmarkType must be TREE or ROCK")
        self.effRadius = 6.7/24 #the radius of a rock
        self.x,self.y,self.landmarkType = (x,y,landmarkType)
        if landmarkType == "TREE":
            self.effRadius = 2.0/12
        else:
            self.effRadius = 6.7/12/2



if __name__ == "__main__":
    print "??"
    testPose = Pose(4.33333333333,2,1)
    print testPose.string()

    testLandmark = Landmark(1,1, "TREE")
    print testLandmark.effRadius