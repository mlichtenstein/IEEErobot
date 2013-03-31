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
        

class Go( Mode ):
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
        state.mode = "Go"
    def act( self, state ):
        nextState = self.makeAMove()
        if nextState == None:
            # Handle error.
            throw Exception( "Need to handle error." )
        if nextState == NEXT_STATE_GRAB:
            return Grab( state )
        if nextState == NEXT_STATE_LOCALIZE:
            return Localize( state )
        return self
    def makeAMove( self, ):
        whatNode = theGuts.whatNode( graph, ( state.pose.x, state.pose.y ) )
        nearestNode = whatNode[0]
        distance = whatNode[1]
        nodeTheta = -180/math.pi* math.atan2(nearestNode.Y-Y,nearestNode.X-X)
        #scoot to the nearest node
        if distance > nearestNode.radius:
            angle =  nodeTheta - theta
            if self.scoot( distance, angle ):
                state.pose.X, state.pose.Y = nearestNode.X, nearestNode.Y
                return NEXT_STATE_GO
            else
                return None
        #face puck and retrieve it
        elif 1 <= nearestNode.puck <= 16:
            return NEXT_STATE_GRAB
        #move along link
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
                else
                    sucess = False
                if not success:
                    return None
            except Exception as e:
                print "Error: ", e
        #update botPose.theta with imu data
        return NEXT_STATE_LOCALIZE
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
            settings.COMMAND_SCOOT, distance, angle  )
        return self.messenger.waitForConfirmation(distance * .5)
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
        return self.messenger.waitForConfirmation(distance * .5)

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
        self.scanUpToDate = False
        self.step = 1
        self.cloudSize = 1000 #approx size of cloud--we will bloom and prune to stay near this
    def act(self, state):
        import localize
        cloud = state.hypobotCloud 
        if self.step == 1:
            print("=========Beginning localization.=========")
            print "step 1: build cloud"
            #add hbots at the current best guess, if nec
            if cloud.count() == 0:
                #cloud.appendGaussianCloud(minCount,state.pose,state.poseUncertainty)
                cloud.appendFlatSquare(self.cloudSize, state.pose, 1.5, 15.0)
            elif cloud.count() < self.cloudSize:
                multiplier = int(self.cloudSize / cloud.count() +.99)
                cloud.appendBloom(multiplier,Pose(.3,.3,3))
            self.step +=1
            return None
        if self.step == 2:
            print "step 2: scan and generate eye data"
            self.messenger.sendMessage(settings.SERVICE_SCAN)
            cloud.clearCollided();
            import time
            messageTime = time.time()
            cloud.generateEyeData(world.World().landmarkList)
            if not self.messenger.checkInBox():
                print("Waiting for scan to finish")
                while not self.messenger.checkInBox():
                    pass
            tup = self.messenger.getMessageTuple()
            self.real_eyeList = localize.messageTupleToEyeList(tup)
            state.eyeList=self.real_eyeList
            self.step +=1
            return None
        if self.step == 3:
            print "step 3: weight hbots"
            cloud.weight(self.real_eyeList, world.World().landmarkList)
            cloud.describeCloud()
            self.step +=1
            return None
        if self.step == 4:
            print "step 4: normalize, average, prune, change bestGuess"
            cloud.normalize()           
            avg = state.hypobotCloud.average()
            cloud.pruneFraction(0.9)
            cloud.describeCloud()
            state.pose = avg
            print "Changing pose to",avg.x,",",avg.y,",",avg.theta
            self.step +=1
            return None
            """
            while True:
                pass
        if self.step == 5:
            print "step 5: prune the cloud, normalize"
            cloud.pruneFraction(0.9)
            cloud.normalize()
            self.step +=1
            return None
        if self.step == 6:
            print "step 6: focus the cloud, weight"
            cloud.appendBloom(3,Pose(.1,.1,1))
            cloud.weight(self.real_eyeList, world.World().landmarkList)
            self.step +=1
            return None
            """
        print state.pose.string()
        import time
        time.sleep(10)
        return Localize(state)
    pass


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

