"""
this library is for the basic building blocks of the representations
our robot uses.
"""

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

class State:
    #The robot's internal state variables go here:
    def __init__(self):
        import time
        import localize
        import copy
        import world
        self.startTime = time.time()
        self.startPause = None
        self.mode = None
        self.moving = False
        self.pose = Pose(.6,.6,0)
        self.poseUncertainty = Pose(.5,.5,20)
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
        self.x,self.y,self.landmarkType = (x,y,landmarkType)
