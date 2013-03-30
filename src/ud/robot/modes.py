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
    """
    Class Tests:
    >>> instance = Go()
    >>> isinstance( instance, Mode )
    True
    """
    def __init__( self , state):
        print("Mode is now Go")
        state.mode = "Go"
    def act(self, state):
        return Go(state)
    pass

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
        self.cloudSize = 500 #approx size of cloud--we will bloom and prune to stay near this
    def act(self, state):
        import localize
        cloud = state.hypobotCloud 
        if self.step == 1:
            print("=========Beginning localization.=========")
            print "step 1: build cloud"
            #add hbots at the current best guess, if nec
            if cloud.count() == 0:
                #cloud.appendGaussianCloud(minCount,state.pose,state.poseUncertainty)
                cloud.appendFlatSquare(self.cloudsize, state.pose, 1,4)
            elif cloud.count() < minCount:
                multiplier = int(minCount / cloud.count() +.99)
                cloud.appendBloom(multiplier,state.poseUncertainty)
            self.step +=1
            return None
        if self.step == 2:
            print "step 2: scan and generate eye data"
            self.messenger.sendMessage(settings.SERVICE_SCAN)
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
            self.step +=1
            return None
        if self.step == 4:
            print "step 4: normalize and average"
            cloud.normalize()           
            avg = state.hypobotCloud.average()
            state.pose = avg
            print "Changing pose to",avg.x,",",avg.y,",",avg.theta
            self.step +=1
            return None
        if self.step == 5:
            print "step 5: prune the cloud"
            state.hypobotCloud.pruneFraction(0.9)
            state.hypobotCloud.normalize()
            self.step +=1
            return None
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
