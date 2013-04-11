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
    graph = None
    def __init__( self , state ):
        state.mode = "Loading..."
    def loadGraph(self, path ):
        try:
            self.graph = theGuts.loadFile( path )
        except (IOError, ImportError,RuntimeError, TypeError, NameError, AttributeError) as e:
            print "load File error"
            #import traceback
            print e
            #traceback.print_stack()
        if self.graph == None:
            self.graph = graph.Graph()
        
    def act(self, state):
        print "attemping to load ~/IEEErobot/src/ud/saveFile"
        self.loadGraph("/home/max/IEEErobot/IEEErobot/src/ud/saveFile")
        #THIS MUST BE CHANGED ON PANDA
        script = "echo robot | sudo -S mkdir /mnt/robo"
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
            state.remainingPucks.append(row)
            self.graph.pucks.append(row)
            for n in self.graph.nodes:
                for p in self.graph.pucks:
                    if not(n.puck==p):
                        n.puck=-1
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
    >>> instance = Go()
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
        import graph
        import math
        whatNode = theGuts.whatNode( state.graph, ( state.pose.x, state.pose.y ) )
        nearestNode = whatNode[0]
        distance = whatNode[1]
        nodeTheta = -180/math.pi* math.atan2(nearestNode.Y- state.pose.y,
                                            nearestNode.X- state.pose.x)
        #scoot to the nearest node
        if distance > nearestNode.radius:
            angle =  nodeTheta - state.pose.theta
            if self.scoot( distance, angle ):
                state.pose.X, state.pose.Y = nearestNode.X, nearestNode.Y
                return self.NEXT_STATE_GO
            else:
                print "!!!"
                return None
        #face puck and retrieve it
        elif 1 <= nearestNode.puck <= 16:
            return self.NEXT_STATE_GRAB
        #move along link
        else:
            try:
                pendingLink = findPath( graph, nearestNode )
                distance = pendingLink.length #in tenths of inches (Matt Bird's pixels)
                if pendingLink == nearestNode.node1:
                    departureAngle = pendingLink.node1direction
                elif pendingLink == nearestNode.node2:
                    departureAngle = pendingLink.node2direction
                angle = departureAngle - theta
                success = True
                if self.rotate( angle ):
                    botPose.theta = nearestNode.theta
                else:
                    success = False
                if success and self.scoot( pendingLink.length ):
                    botPose.X = nearestNode.X
                    botPose.Y = nearestNode.Y
                else:
                    sucess = False
                if not success:
                    return None
            except Exception as e:
                print "Error: ", e
        #update botPose.theta with imu data
        return Localize(state)
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
        messageID = self.messenger.sendMessage( settings.SERVICE_GO, \
            settings.COMMAND_SCOOT, int(distance), angle  )

        self.state.hypobotCloud.scootAll(distance, angle)
        return self.messenger.waitForConfirmation(messageID, distance) #send the distance in pixels (ie tentsh of inches)
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
        self.messenger.waitForConfirmation(distance)


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
        Localize.nextStep = Scan() #we only want to prime the cloud once
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
        return Scan() #REPLACE WITH GoToPathfind()
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
        self.thisStep = PrimeCloud()
    def act(self, state):
        nextStep = self.thisStep.do(self, state)
        if nextStep == None:
            return Go(state)
        else:
            self.thisStep = nextStep
            return Go(state)


"""========================================================================================="""
"""/\/\/\/\/\/\/\/\/\/\/\/\/\  THUS ENDS LOCALIZATION  /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/"""
"""========================================================================================="""


class Grab( Mode ):
    # Defualt position
    POSITION1 = "60,90,60"
    POSITION2 = ""
    # Waiting position.
    POSITION3 = "90,0,90"
    """
    Class Tests:
    >>> instance = Grab()
    >>> isinstance( instance, Mode )
    True
    """
    def __init__( self , state):
        print("Mode is now Grab")
        state.mode = "Grab"
	self.state = state
    def act():
	leString = self.grab();
	messageID = self.messenger.sendmessage( 'G', leString )
	self.messenger.waitForConfirmation( messageID, 5 )
	messageID = self.messenger.sendmessage( 'G', POSITION1 )
	self.messenger.waitForConfirmation( messageID, 5 )
	messageID = self.messenger.sendmessage( 'G', POSITION2 )
	self.messenger.waitForConfirmation( messageID, 5 )
	messageID = self.messenger.sendmessage( 'G', POSITION3 )
	self.messenger.waitForConfirmation( messageID, 5 )
	return Localize( self.state )
	
    def grab():
	    #circle detection inverse sensitivity (20 for low light)
	    canny_threshold = 100

	    #set up camera VideoCap(arg) might need to be 0 on panda
	    cap = cv2.VideoCapture(1)

	    cv2.namedWindow('test',1)

	    # show video on screen for testing
	    while True:
		    flag, frame = cap.read()
		    cv2.imshow('test', frame)
		    ch = 0xFF & cv2.waitKey(1)
		    if ch != 0xFF:
			    break
	    src_gray = cv2.cvtColor( frame, cv.CV_BGR2GRAY )
	    src_gray = cv2.GaussianBlur( src_gray,(9,9), 2  )
	    print src_gray.shape
	    # this line will throw an exception if it fails to find a circle
	    circles = cv2.HoughCircles( src_gray, cv.CV_HOUGH_GRADIENT,1, 30 , param1=canny_threshold, param2=100)

	    #this paints the cricles that were found in a window
	    #the robot doesnt need this
	    for cir in circles[0]:
		    print cir
		    somePointx = cv.Round(cir[0])
		    somePointy = cv.Round(cir[1])
		    radius = cv.Round(cir[2])
		    cv2.circle( frame, (somePointx, somePointy), 3,(0,255,0), -1, 8, 0 )
		    cv2.circle( frame, (somePointx, somePointy), radius, (0,0,255), 3, 8, 0 )

	    cv2.namedWindow('farts', 1)
	    cv2.imshow('farts', frame)
	    cv2.waitKey(0)

	    #arm segment lengths (d = vertical offset)
	    a2 = 5 
	    a3 =7.85
	    d = 7.5

	    #scale view size src_gray.shape to physical area
	    #scaling factor = view size / inches of area 
	    x = (cir[0] - 113) / 28 
	    y = (261.8 - cir[1]) / 29.1
	    z = .45 #disk height offset

	    print "x = {0} y = {1}".format(x,y)

	    r = math.hypot(x,y)
	    s = z - d

	    theta1 = (math.atan2(y,x))*57.2957795
	    D = ((r*r) + (s*s) -(a2*a2) - (a3*a3))/(2*a2*a3)
	    theta3 = math.atan2(-math.sqrt(1 - D*D),D)
	    theta2 = math.atan2(s, r) -math.atan2(a3*math.sin(theta3), a2+a3*math.cos(theta3))
	    theta3 = -(theta3 * 57.2957795 )
	    theta2 = theta2 * 57.2957795 + 90

	    return  '{0},{1},{2}'.format(theta1, theta2, theta3)


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
import cv2
import cv
import numpy
import math
import serial

