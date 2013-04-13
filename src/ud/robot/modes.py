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
        
        
class Go( Mode ):
    MS_PER_FOOT = 4000
    NEXT_STATE_GO = 0
    NEXT_STATE_GRAB = 1
    NEXT_STATE_LOCALIZE = 2
    """
    Class Tests:
    >>> instance = Go()distance
    >>> isinstance( instance, Mode )
    True
    """
    def __init__( self , state):
        import theGuts
        print("Mode is now Go")
        self.state = state
        state.mode = "Go"
    def act( self, state ):
        nextState = self.makeAMove(state)
        if nextState == None:
            # Handle error.
            raise Exception( "Need to handle error." )
        if nextState == self.NEXT_STATE_GRAB:
            return Grab( state )
        if nextState == self.NEXT_STATE_LOCALIZE:
            return Localize( state )
        return self
    def makeAMove( self, state):

        """
        decides between 3 actions:  Grab, travel along path, go to path.
        """
        import theGuts
        import math
        whatNode = theGuts.whatNode( self.graph, ( state.pose.x, state.pose.y ) )
        nearestNode = whatNode[0]
        distance = whatNode[1]
        nodeTheta = 180/math.pi* math.atan2(nearestNode.Y- state.pose.y,
                                            nearestNode.X- state.pose.x)
        #scoot to the nearest node
        if distance > nearestNode.radius:
            print "scooting back onto graph"
            angle =  nodeTheta - state.pose.theta
            if self.scoot( distance, angle ):
                state.pose.X, state.pose.Y = nearestNode.X, nearestNode.Y
                return self.NEXT_STATE_LOCALIZE
            else:
                print "!!!"
                return None
        #face puck and retrieve it
        elif 1 <= nearestNode.puck <= 16:
            print "INSERT CODE THAT ROTATES TO FACE node.theta THEN GRAB"
            return self.NEXT_STATE_GRAB
        #move along link
        else:
            print "moving along link"
            try:
                pendingLink = theGuts.findPath( self.graph, nearestNode )
                distance = pendingLink.length #in tenths of inches (Matt Bird's pixels)
                if pendingLink.node1 == nearestNode:
                    departureAngle = self.rectifyAngle(int(pendingLink.node1direction))
                elif pendingLink.node2 == nearestNode:
                    departureAngle = self.rectifyAngle(int(pendingLink.node2direction))
                print "departure angle is",departureAngle,"and pose theta is",state.pose.theta
                rectifiedPoseTheta = self.rectifyAngle(state.pose.theta)
                print rectifiedPoseTheta
                angle = rectifiedPoseTheta - departureAngle
                success = True
                print "about to rotate..."
                if self.rotate( angle ):
                    print "updating angle"
                    state.pose.theta = departureAngle
                else:
                    print "this is what made success false"
                    success = False
                destinationNode = theGuts.getOtherNode(pendingLink,nearestNode)
                scootAngle = 180/math.pi* math.atan2(nearestNode.Y- destinationNode.Y,
                                            nearestNode.X- destinationNode.X)
                scootAngle = self.rectifyAngle(scootAngle)
                print "made it here"
                if success and self.scoot( distance, scootAngle ):
                    print "but not here"
                    state.pose.X = nearestNode.X
                    state.pose.Y = nearestNode.Y
                else:
                    sucess = False
                if not success:
                    return None
            except Exception as e:
                print "Error: ", e
        #update botPose.theta with imu data
        return self.NEXT_STATE_LOCALIZE

    def rectifyAngle(self, angle):
        while angle>180:
            angle-=360
        while angle<-180:
            angle+=360
        return angle    

    def scoot( self, distance, angle ):
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
        print "ordering a scoot of",distance/120,"feet at",angle,"degrees."
        messageID = self.messenger.sendMessage( settings.SERVICE_GO, \
            settings.COMMAND_SCOOT, int(distance), angle  )
        #EG send ":T0,S,120,0;"

        self.state.hypobotCloud.scootAll(distance, angle)
        return self.messenger.waitForConfirmation(messageID, distance*settings.MS_PER_FOOT/120000 + 1) 
    def rotate( self, angle ):          
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
        messageID = self.messenger.sendMessage( settings.SERVICE_GO, \
            settings.COMMAND_TURN, angle  )
        self.state.hypobotCloud.rotateAll(angle)
        self.messenger.waitForConfirmation(messageID, abs(angle) * settings.MS_PER_DEGREE/1000 + 1) 


"""========================================================================================="""
"""/\/\/\/\/\/\/\/\/\/\/\/\/\/\  HERE BE LOCALIZATION  /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/"""
"""========================================================================================="""

class LocStep: #A step is any object with a .do method.  Included only as a template.
    def do(self, mode, state):
        pass
class PrimeCloud(LocStep):
    def do(self, mode, state):
        print("=========Beginning localization.=========")
        print "Priming cloud in sector 1..."
        #add hbots at the current best guess, if nec
        state.hypobotCloud.appendFlatSquare(state.hypobotCloud.cloudSize, state.pose, .50, 10.0)
        Localize.thisStep = Scan() #we only want to prime the cloud once
        return ClearCollided()
class CleanAndBoostCloud(LocStep):
    def do(self,mode,state):
        self.hypobotCloud.clearCollided()
        while state.hypobotCloud.count() < state.hypobotCloud.cloudSize:
            print "repopulating cloud..."
            hypobotCloud.appendBoost(robotbasics.Pose(.5,.5,10))
class ClearCollided(LocStep):
    def do(self, mode, state):
        print "clearing out collided hbots"
        state.hypobotCloud.clearCollided();
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
        self.real_eyeList = localize.messageTupleToEyeList(tup)
        state.eyeList=self.real_eyeList
        return WeightCloud()
class WeightCloud(LocStep):
    def do(self, mode, state):
        print "weighting hbots..."
        state.hypobotCloud.weight(state.eyeList, world.World().landmarkList)
        state.hypobotCloud.describeCloud()
        return AverageCloud()
class AverageCloud(LocStep):
    def do(self, mode, state):
        print "averaging cloud... "
        state.hypobotCloud.normalize()           
        avg = state.hypobotCloud.average()
        state.hypobotCloud.describeCloud()
        state.pose = avg
        print "Changing pose to",avg.x,",",avg.y,",",avg.theta
        return PruneAndBoost()
class PruneAndBoost(LocStep):
    def do(self, mode, state):
        print "pruning and boosting..."
        state.hypobotCloud.pruneThreshold(0.5) #approx 1 sigma
        while state.hypobotCloud.count() < state.hypobotCloud.cloudSize:
            state.hypobotCloud.appendBoost(state.poseUncertainty)
        state.hypobotCloud.flatten()
        return GoToPathfind()
class GoToPathfind(LocStep):
    def do(self, mode, state):
        return None #escapes to next mode

class Localize( Mode ):
    """
    Class Tests:
    >>> instance = Localize()
    >>> isinstance( instance, Mode )
    True
    """
    def __init__( self , state):
        print("Mode is now Localize")
        state.mode = "Localize"
        self.thisStep = GoToPathfind() #use for fast testing,
        #self.thisStep = PrimeCloud() #use for real operation
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
