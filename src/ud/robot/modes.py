"""
This library contains the actions that robot will want to perform as it
moves through its' modes.  It basically defines a finite state machine where
"state" is the input (I know that's weird language, sorry) and mode.act() is the
output.
"""

from robotbasics import *
import settings
import world
import csv
import subprocess
import theGuts
import graph
import math

"""
Module Tests:
"""

class Mode:
    """
    Initializes the robot and provides a base of functionality to build on
     and override via polymorphism.
    Class Tests:
    >>> instance = Mode()
    """
    graph = None
    nearestPuck = -1 #will change later
    # REQUIRED: Holds the messenger that connects to the arduino layer.
    messenger = None
    # REQUIRED: Holds the function which signals a change of modes.
    signalNewMode = None
    def __init__( self, state ):
        """
        Get the robot setup to go."
        """
        raise Exception( "Please write your wonderful code here." )
    def onMessageReceived( self, message ):
        if __debug__ and not isinstance( message, str ):
            raise TypeError, "Bad arguments: Should be a \"str\" type."
        import settings
        category = message[0]
        print message
        if category == settings.SERVICE_IRSENSOR_POLL:
            self.onIRReadingReceived( utility.Reading( message ) )
    def onIRReadingReceived( self, reading ):
        if __debug__ and not isinstance( message, utility.Reading ):
            raise TypeError, "Bad arguments: Should be a \"utility.Reading\" type."
    def act( self, state ):
        """
        The robot takes action based on the the state. Please override in any 
        inheriting classes that you need.
        
        Arguments:
        robotStatus -- contains information such as position, mode, ect.
        """
        raise Exception( "Please write your wonderful code here." )
    def begin( self ):
        """
        Description
            The main loop will trigger this event at the start of a new mode.
             Feel free to override.
        """
        pass
    def end( self ):
        """
        Description
            The main loop will trigger this event at the end of the mode.
             Feel free to override.
        """
        pass
    
    def onConfirmation( self, confirmationID ):
        """
        Description
            Triggered by the main loop when a confirmation message is received. 
             To use the event, simply overwrite this method in a child class.
        Parameters
            confirmationID -- is the ID number of the message.
        """
        pass
    def onMessage( self, fields ):
        """
        Description
            Triggered by the main loop when message is received that is NOT
             handled in the above message events. To use the event, simply 
             overwrite this method in a child class. 
        Parameters
            fields -- a list of message parts.
        """
        pass
    
#opens graph from file, and opens usb, then preps the graph for use
class LoadAll( Mode):
    #graph = None
    def __init__( self , state ):
        state.mode = "Loading..."
    def loadGraph(self, path ):
        try:
            self.graph = theGuts.loadFile( path )
            Mode.graph = self.graph
        except (IOError, ImportError,RuntimeError, TypeError, NameError, AttributeError) as e:
            print "load File error"
            #import traceback
            print e
            #traceback.print_stack()
        if self.graph == None:
            self.graph = graph.Graph()
        
    def act(self, state):
        print "attemping to load ~IEEErobot/IEEErobot/src/ud/saveFile.graph"
        try:
            self.loadGraph("/home/max/IEEErobot/IEEErobot/src/ud/saveFile.graph")
            #THIS MUST BE CHANGED ON PANDA
            script = "echo rty456 | sudo -S mkdir /mnt/robo"
            proc = subprocess.Popen(['bash', '-c', script],
                                    stdout=subprocess.PIPE)
            stdout = proc.communicate()
            script = "echo rty456 | sudo -S mount /dev/disk/by-label/IEEER5 /mnt/robo"
            #replace rty456 with robot
            proc = subprocess.Popen(['bash', '-c', script], 
                stdout=subprocess.PIPE)
            stdout = proc.communicate()
            USB = open("/mnt/robo/Locatio.csv")
            reader = csv.reader(USB)
        except:
            print "Could not read thumb drive. Using full puck list."
            reader=[[1,2,3,4,5,6,7,8,9,10,11,12,13,15,16],]
        self.graph.pucks=list()
        for row in reader:
            for r in row:
                state.remainingPucks.append(int(r))
                self.graph.pucks.append(int(r))
        print self.graph.pucks
        for n in self.graph.nodes:
            temp = -1
            for p in self.graph.pucks:
                if n.puck==p:
                    temp = p
                    print temp
            n.puck=temp
        return Localize(state)
        
class Ready( Mode):
    """
    the state that the robot sits in while it waits for the judge to press
    the start button.  It must poll the arduino, waiting for an indication
    of such an event.
    """
    def __init__( self , state):
        print("Mode is now Ready")
        state.mode = "Ready"
    def act(self, state):
        #put a while loop here that polls arduino and breaks upon
        #"Start" command
        return ReadUSBDrive(state)
        

"""========================================================================================="""
"""                                            GO                                          """
"""========================================================================================="""

"""NOTES ABOUT THIS TRANSPARENTIZATION, by max
The main mechanism behind transparentization is to break the act() up into steps.
EAch time you call act(), it does the do() 
in go.thisStep.  The do() does some stuff, and returns the next step.  It's like 
a finite state machine, where each state determines the next state.
If you return none, the Act will try to go to its nextMode.
(this makes it go back to the beginning of that step.)  To escape the Go, you should
change mode.nextMode to the next mode you want, then return none.  By default it localizes.

One drawback is that variables do not, by default, carry to the next step.  The
way around this is to make persistent variables attributes of the mode instance,
so distance became mode.distance.  Also, what used to be self now refers to the step,
not the mode, so self.rectifyAngle is now mode.rectifyAngle.
"""

class GoStep: #A step is any object with a .do method.  Included only as a template.
    def do(self, mode, state):
        pass

class ExamineCurrentPose(GoStep):
    """
    This step is a sorter--it looks at the current pose, then
    decides between going to Grab, moving to a node, or moving
    along a link.
    """
    def do(self,mode,state):
        import copy
        print "deciding where to go next..."
        whatNode = theGuts.whatNode( mode.graph, ( state.pose.x*120, state.pose.y *120) )
        mode.nearestNode = whatNode[0]
        state.nearestPuck = mode.nearestNode.puck
        mode.distance = whatNode[1]
        mode.nodeTheta = 180/math.pi* math.atan2(mode.nearestNode.Y - state.pose.y*120,
                mode.nearestNode.X - state.pose.x*120)
                #nodeTheta is postive in CW direction
        #If we're off-graph, scoot to the nearest node
        print "nearest node is",mode.nearestNode.string()
        if mode.distance > mode.nearestNode.radius:
            return GetOnGraph()
        #If we're close to a puck, turn to face it
        elif 1 <= mode.nearestNode.puck <= 16:
            return FacePuck()#also goes to grab
        #If none of the above occured, it's time to move along the path
        else:
            return RotateToMoveAlongLink()

class GetOnGraph(GoStep):
    def do(self,mode,state):
        print "Bot seems to be off-graph.  Trying to get back on"
        angle =  mode.nodeTheta + state.pose.theta
        if not mode.scoot(state,  mode.distance, angle ):
            print "scoot failed! Going to Localize..."
        return GoToLocalize()

class FacePuck(GoStep):
    def do(self,mode,state):
        print "Turning to face puck"
        angle = mode.rectifyAngle(mode.nearestNode.theta+state.pose.theta)
        mode.rotate(state, angle)
        Mode.nearestPuck = mode.nearestNode.puck
        mode.nextMode = Grab(state) #go to grab
        return None 

class RotateToMoveAlongLink(GoStep):
    def do(self,mode,state):
        print "rotating to align with nearest node's departure angle..."
        mode.pendingLink = theGuts.findPath( mode.graph, mode.nearestNode )
        mode.distance = mode.pendingLink.length #in tenths of inches (Matt Bird's pixels)
        #pick which node to aim for
        if mode.pendingLink.node1 == mode.nearestNode:
            departureAngle = mode.rectifyAngle(int(mode.pendingLink.node1direction))
            print "the destination node is",mode.pendingLink.node1.string()
        elif mode.pendingLink.node2 == mode.nearestNode:
            departureAngle = mode.rectifyAngle(int(mode.pendingLink.node2direction))
            print "the destination node is",mode.pendingLink.node2.string()
        print "departure angle is",departureAngle,"and pose theta is",state.pose.theta
        angle =  departureAngle + state.pose.theta
        angle = mode.rectifyAngle(angle)
        print "about to rotate..."
        if mode.rotate(state,  angle ):
            print "updating angle to",state.pose.theta - angle,"ie",departureAngle
            return ScootAlongLink()
        else:
            mode.nextMode = Localize(state)
            return None

class ScootAlongLink(GoStep):
    def do(self,mode,state):
        print "Scooting along link..."
        destinationNode = theGuts.getOtherNode(mode.pendingLink,mode.nearestNode)
        scootAngle = 180/math.pi* math.atan2(-mode.nearestNode.Y+ destinationNode.Y,
                -mode.nearestNode.X+ destinationNode.X) + state.pose.theta
        scootAngle = mode.rectifyAngle(scootAngle)
        print "scootAngle=",scootAngle
        mode.scoot(state,  mode.distance, scootAngle )
        print "updating position to",state.pose.string()
        mode.nextMode = Localize(state)
        return None

class GoToLocalize(GoStep):
    def do(self,mode,state):
        mode.nextMode = Localize(state)
        return None

class Go( Mode ):
    """
    Class Tests:
    >>> instance = Go()
    >>> isinstance( instance, Mode )
    True
    """
    thisStep = ExamineCurrentPose()
    #thisStep = GoToLocalize()
    def __init__( self , state):
        import theGuts
        print("Mode is now Go")
        print("==========Beginning Go=========")
        print "Current best guess pose is",state.pose.string()
        self.state = state
        state.mode = "Go"
    def act( self, state ):
        #the action happens in this line:
        nextStep = self.thisStep.do(self, state)
        #this part parses the return from nextStep, and decides
        #whether to go to a new step or a new mode
        if nextStep == None:
            if self.nextMode == None:
                return Loalize(state) #the default new state is localize
            else:
                return self.nextMode
        else:
            self.thisStep = nextStep
            return self

    def rectifyAngle(self, angle):
        while angle>180:
            angle-=360
        while angle<-180:
            angle+=360
        return angle    

    def scoot( self, state, distance, angle ):
        """
        Description
            Sends a scoot command to the Arduino and waits for the confirmation
             message indicating the operation was a success. Failure will be
             caused when the timer expired or the wrong confirmation id was
             received. The wrong confirmation ID is very unlikely.
        Parameters
            distance -- the distance of the traverse.
            angle -- the theta on the traverse.
        Return
            True -- when the operation is a success.
            False -- when the operation failed.
        """
        angle = self.rectifyAngle(angle)
        print "ordering a scoot of",distance/120,"feet at",angle,"degrees from heading."
        messageID = self.messenger.sendMessage( settings.SERVICE_GO, \
            settings.COMMAND_SCOOT, int(distance), angle  )
        #EG send ":T0,S,120,0;"
        if self.messenger.waitForConfirmation(messageID, 
                distance*settings.MS_PER_FOOT/12000 + 1):
            self.state.hypobotCloud.scootAll(distance/120, -angle)
            scootAngle = angle - state.pose.theta
            state.pose.x = state.pose.x + distance/120*math.cos(scootAngle*math.pi/180)
            state.pose.y = state.pose.y + distance/120*math.sin(scootAngle*math.pi/180)
            return True
        else:
            print "No confirmation of scoot!"
            return False     
    def rotate( self, state, angle ):          
        """
        Description
            Sends a scoot command to the Arduino and waits for the confirmation
             message indicating the operation was a success. Failure will be
             caused when the timer expired or the wrong confirmation id was
             received. The wrong confirmation ID is very unlikely.
        Parameters
            angle -- the theta on the traverse.
        Return
            True -- when the operation is a success.
            False -- when the operation failed.
        """
        print "ordering a rotate of",angle,"degrees."
        messageID = self.messenger.sendMessage( settings.SERVICE_GO, \
            settings.COMMAND_TURN, angle  )
        if self.messenger.waitForConfirmation(messageID, 
                abs(angle) * settings.MS_PER_DEGREE/100 + 1): #NOTE:  This timeout
                #has been increased by a factor of 10 to work around an unsquashed bug
            self.state.hypobotCloud.rotateAll(-angle)
            state.pose.theta -= angle
            return True
        else:
            print "No confirmation of rotate!"
            return False


"""========================================================================================="""
"""/\/\/\/\/\/\/\/\/\/\/\/\/\/\  HERE BE LOCALIZATION  /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/"""
"""========================================================================================="""

class LocStep: #A step is any object with a .do method.  Included only as a template.
    def do(self, mode, state):
        pass
class PrimeCloud(LocStep):
    def do(self, mode, state):
        if state.hypobotCloud.count() == 0:
            print "No hypobots in cloud!  Priming cloud at current best-guess pose..."
            #add hbots at the current best guess, if nec
            state.hypobotCloud.appendFlatSquare(state.hypobotCloud.cloudSize, state.pose, .50, 10.0)
            return RepopulateCloud()    
        else:
            print "Cloud does not need priming."
            return RepopulateCloud()
class RepopulateCloud(LocStep):
    def do(self,mode,state):
        print "clearing collisions, repopulating cloud..."
        state.hypobotCloud.clearCollided()
        while state.hypobotCloud.count() < state.hypobotCloud.cloudSize:
            state.hypobotCloud.resampleOneWithGaussian(Pose(.1,.1,5))
        state.hypobotCloud.normalize()
        #state.hypobotCloud.normalize()
        return Scan()
class Scan(LocStep):
    def do(self, mode, state):
        print "scanning and generating eye data..."
        mode.messenger.sendMessage(settings.SERVICE_SCAN)
        
        import time
        import localize
        messageTime = time.time()
        state.hypobotCloud.generateEyeData(world.World().landmarkList)
        if not mode.messenger.checkInBox():
            print("Waiting for scan to finish")
            while not mode.messenger.checkInBox():
                pass
        tup = mode.messenger.getMessageTuple()
        mode.messenger.waitForConfirmation(tup[1],5.0)
        self.real_eyeList = localize.messageTupleToEyeList(tup)
        state.eyeList=self.real_eyeList
        return WeightCloud()
class WeightCloud(LocStep):
    def do(self, mode, state):
        print "weighting hbots..."
        state.hypobotCloud.weight(state.eyeList, world.World().landmarkList)
        state.hypobotCloud.describeCloud()
        state.hypobotCloud.normalize()
        return GetNewPose()
class GetNewPose(LocStep):
    def do(self, mode, state):
        print "getting new best guess pose... "
        peak = state.hypobotCloud.getPeakBot()
        #state.hypobotCloud.describeCloud()
        state.pose = peak.pose
        print "state.poseA",state.pose
        print "Changing pose to",peak.pose.x,",",peak.pose.y,",",peak.pose.theta
        return PruneAndBoost()
class PruneAndBoost(LocStep):
    def do(self, mode, state):
        print "pruning and boosting..."
        state.hypobotCloud.pruneFraction(0.32) #approx 1 sigma
        while state.hypobotCloud.count() < state.hypobotCloud.cloudSize:
            state.hypobotCloud.resampleOne()
        return GoToPathfind()
class GoToPathfind(LocStep):
    def do(self, mode, state):
        print "switching to go...."
        return None #escapes to next mode

class Localize( Mode ):
    """
    Class Tests:
    >>> instance = Localize()
    >>> isinstance( instance, Mode )
    True
    """
    #thisStep = GoToPathfind() #use for fast testing,
    thisStep = PrimeCloud() #use for real operation
    def __init__( self , state):
        print("Mode is now Localize")
        print("=========Beginning localization.=========")
        state.mode = "Localize"
    def act(self, state):
        nextStep = self.thisStep.do(self, state)
        if nextStep == None:
            return Go(state)
        else:
            self.thisStep = nextStep
            return self


"""========================================================================================="""
"""/\/\/\/\/\/\/\/\/\/\/\/\/\  THUS ENDS LOCALIZATION  /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/"""
"""========================================================================================="""


class Grab( Mode ):
    """
    Class Tests:
    >>> instance = Grab()
    >>> isinstance( instance, Mode )
    True
    """
    def __init__( self , state):
        print("Mode is now Grab")
        state.mode = "Grab"
    pass
    def act(self, state):
        print "PRETENDING TO GRAB PUCK, INSERT REAL GRAB CODE HERE"
        for node in self.graph.nodes:
            if node.puck == state.nearestPuck:
                node.puck = -1
        Mode.graph = self.graph
        state.remainingPucks.remove(state.nearestPuck)
        Mode.nearestPuck = -1
        return Go(state)


# Only run when someone specifically runs this module.
if __name__ == "__main__":
    """
    This shows how to use the architecture to scan. First a 
     scan message is sent to start the scan. Next, each reading
     is sent to the mode. I would expect this code 
     to be modified to meet the needs of the team.
    
    I have noticed that the last message received is too small.
    """
    # Needed libraries.
    import utility
    import settings
    # Initialize the mode.
    state = State()
    mode = Localize(state)
    # Open the port and initialize contact.
    messenger = utility.Messenger( utility.SerialPort() )
    # Request the scan.
    messenger.sendMessage( settings.SERVICE_SCAN )
    # Check for messages. Pass any messages to the mode.
    while True:
        if messenger.checkInBox():
            mode.onMessageReceived( messenger.getMessage() )
