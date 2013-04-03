"""
This library contains the actions that robot will want to perform as it
moves through its' modes.  It basically defines a finite state machine where
"state" is the input (I know that's weird language, sorry) and mode.act() is the
output.
"""

from robotbasics import *
import settings
import world

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
        
class ReadUSBDrive( Mode):
    def __init__( self , state):
        print("Mode is now ReadUSB")
        state.mode = "ReadUSB"
    def act(self, state):
        print("Write code that reads from the USB here")
        if state.hypobotCloud.count() == 0:
            state
        return Localize(state)
        
class GoScoot( Mode ):
    """
    Description
        This class will move the robot along a vector on the map. It will be
         switched to from the GoOnGraph or GoOffGraph modes. The class retains
         a reference to the mode switched from so that upon completion or
         failure of its operation, it can switch back. The switching behavior
         resembles function calls.

       The vector must be chopped into smaller vectors. This is necessary in
        the case where the IMU sends back data that does not agree with the
        expected effect of movement. In that case, the robot may cease its
        movement and do a localization.
    """
    SUBDISTANCE = 5
    confirmationIDNeeded = None
    completedSubOperations = 0
    def __init__( self , state, distance, destinationXY, nextMode ):
        self.state = state
        self.nextMode = nextMode
        self.distance = distance 
        self.destinationXY = destinationXY
        # There will n equal distances and n + 1 distances. So one will be 
        #  larger than the rest.
        self.n = int( distance / SUBDISTANCE )
        # XXX need to make sure for floats that modulus gets a
        #  floating number less than 5 which is the remainder.
        # The last distance will be the remainder and larger than the rest.
        self.lastScoot = distance % SUBDISTANCE

    def begin( self ):
        scoot( SUBDISTANCE ) 
    def scoot( self, distance ):
        self.confirmationIDNeeded = self.messenger.sendMessage(  \
            settings.SERVICE_GO, settings.COMMAND_SCOOT, distance )
    def onConfirmation( self, confirmationID ):
        """
        Description
            Triggered by the main loop when a confirmation message is received.
            XXX
        Parameters
            confirmationID -- is the ID number of the message.
        """
        if self.confirmationIDNeeded != None and \
         confirmationID == self.confirmationIDNeeded:
            # XXX need to update the x and y position each time.
            self.confirmationIDNeeded = None
            self.completedSubOperations = self.completedSubOperations + 1
            # Equal distances.
            if self.completedSubOperations < self.n:
                scoot( SUBDISTANCE ) 
            # The last distance.
            elif self.completedSubOperations == self.n:
                scoot( self.lastScoot ) 
            # Rotation complete.
            else:
                state.pose.X, state.pose.Y = self.destinationXY
                signalNewMode( nextMode )
class GoRotate( Mode ):
    """
    Description
        This class represents the mode of the robot when it is rotating by a
         certain angle. Will be swithced to from GoOnGraph or GoOffGraph. The
         class retains a reference to the mode switched from so that upon
         completion or failure of its operation, it can switch back. The
         switching behavior resembles function calls.
         
        The class has to chop the whole rotation angle into lots of smaller
         angles. This is necessary in the case where the IMU sends back data
         that does not agree with the expected effect of rotation. In that
         case the robot may cease its rotation and do a localization.
    """
    SUBANGLE = 5
    confirmationIDNeeded = None
    completedSubOperations = 0
    def __init__( self, state, angle, destinationTheta, nextMode ):
        self.state = state
        self.nextMode = nextMode
        self.angle = angle
        self.destinationTheta = destinationTheta
        # There will n equal angles and n + 1 angles. So one will be larger
        #  than the rest.
        self.n = int( angle / SUBANGLE )
        # XXX need to make sure for floats that modulus gets a
        #  floating number less than 5 which is the remainder.
        # The last angle will be the remainder and larger than the rest.
        self.lastAngle = angle % SUBANGLE

    def begin( self ):
        rotate( SUBANGLE ) 
    def rotate( self, angle ):
        self.confirmationIDNeeded = self.messenger.sendMessage(  \
            settings.SERVICE_GO, settings.COMMAND_TURN, angle )
    def onConfirmation( self, confirmationID ):
        """
        Description
            Triggered by the main loop when a confirmation message is received.
            XXX
        Parameters
            confirmationID -- is the ID number of the message.
        """
        if self.confirmationIDNeeded != None and \
         confirmationID == self.confirmationIDNeeded:
            # XXX need to update the theta pose each time.
            self.confirmationIDNeeded = None
            self.completedSubOperations = self.completedSubOperations + 1
            # Equal angle sizes.
            if self.completedSubOperations < self.n:
                rotate( SUBANGLE ) 
            # The last angle.
            elif self.completedSubOperations == self.n:
                rotate( self.lastAngle ) 
            # Rotation complete.
            else:
                state.pose.theta = self.destinationTheta
                signalNewMode( nextMode )

class GoOnGraph( Mode ):
    """
    Description
        This class represents the mode of the robot when its calculatably
         within the nodes and links of the tacticle plan. The mode will
         switch to the GoRotate and GoScoot modes as needed for each link
         in its path until it has reached the target node.
    """
    # Theta tolerance is maximum theta diff in degrees b/t the node and actual.
    THETA_TOLERANCE = 1
    # Distance tolerance is maximum dist diff b/t the node and actual.
    DISTANCE_TOLERANCE = 1
    
    # BEGIN Next State enum.
    NEXT_STATE_GO = 0
    NEXT_STATE_GRAB = 1
    NEXT_STATE_LOCALIZE = 2
    # END Next State enum.
    
    def __init__( self , state):
        import theGuts
        print("Mode is now Go")
        state.mode = "Go"
        self.confirmationIDNeeded = None
    def act( self, state ):
        self.makeAMove()
        # Do not switch states by default.
        return None 
        
    def makeAMove( self, ):
        """
        decides between 3 actions:  Grab, travel along path, go to path.
        """
        whatNode = theGuts.whatNode( graph, ( state.pose.x, state.pose.y ) )
        nearestNode = whatNode[0]
        distance = whatNode[1]
        nodeTheta = -180/math.pi* math.atan2(nearestNode.Y-Y,nearestNode.X-X)
        thetaDiff = nodeTheta - botPose.theta
        # Turn to view the puck then pickup.
        elif 1 <= nearestNode.puck <= 16:
            # First turn to face the node.
            thetaDiff = nearestNode.theta - botPose.theta
            if abs( nearestNode.theta - botPose.theta ) > THETA_TOLERANCE:
                signalNewMode( Rotate( state, thetaDiff, \
                    nearestNode.theta, self ) )
                return
            # Next switch to the grab mode.
            signalNewMode( Grab( state ) )
            return
        else:
            try:
                pendingLink = findPath( graph, nearestNode )
                distance = pendingLink.length
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
class GoOffGraph( Mode ):
    """
    Description
        This class represents the mode where the robot is too far off from the
         links and nodes of the tacticle plan. In this off-road mode the robot
         tries to re-align itself onto the nearest node or link. 
    """
    def begin( self ):
        whatNode = theGuts.whatNode( graph, ( state.pose.x, state.pose.y ) )
        nearestNode = whatNode[0]
        distance = whatNode[1]
        nodeTheta = -180/math.pi* math.atan2(nearestNode.Y-Y,nearestNode.X-X)
        thetaDiff = nodeTheta - botPose.theta
        # First turn to face the node.
        if abs( thetaDiff ) > THETA_TOLERANCE:
            #self.rotate( thetaDiff )
            self.status = STATUS_TURNING
            self.destinationTheta = nodeTheta
            signalNewMode( \
                Rotate( state, thetaDiff, self.destinationTheta, self ) )
            return
        signalNewMode( Rotate( state, distance, \
            ( nearestNode.X, nearestNode.Y ), self ) )
        signalNewMode( Localize( state ) )
    pass
class Go( Mode ):
    """
    Class Tests:
    >>> instance = Go()
    >>> isinstance( instance, Mode )
    True
    """
    # Theta tolerance is maximum theta diff in degrees b/t the node and actual.
    THETA_TOLERANCE = 1
    # Distance tolerance is maximum dist diff b/t the node and actual.
    DISTANCE_TOLERANCE = 1
    
    # BEGIN Next State enum.
    NEXT_STATE_GO = 0
    NEXT_STATE_GRAB = 1
    NEXT_STATE_LOCALIZE = 2
    # END Next State enum.
    
    def __init__( self , state):
        import theGuts
        print("Mode is now Go")
        state.mode = "Go"
        self.confirmationIDNeeded = None
    def act( self, state ):
        self.makeAMove()
        # Do not switch states by default.
        return None 
        
    def makeAMove( self, ):
        whatNode = theGuts.whatNode( graph, ( state.pose.x, state.pose.y ) )
        nearestNode = whatNode[0]
        distance = whatNode[1]
        nodeTheta = -180/math.pi* math.atan2(nearestNode.Y-Y,nearestNode.X-X)
        thetaDiff = nodeTheta - botPose.theta
        
        # Off graph so scoot to the nearest node.
        if distance > nearestNode.radius:
            signalNewMode( TraverseOffGraph( state ) )
            return

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
        state.hypobotCloud.appendFlatSquare(state.hypobotCloud.cloudSize, state.pose, 10.0, 225.0)
        Localize.nextStep = Scan() #we only want to prime the cloud once
        return ClearCollided()
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
        state.hypobotCloud.pruneFraction(0.32) #approx 1 sigma
        while state.hypobotCloud.count() < state.hypobotCloud.cloudSize:
            state.hypobotCloud.appendBoost(state.poseUncertainty)
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
            return None #come bak to Localize


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
