
                        # Port description:
PORT = "/dev/ttyACM0"
                        # Message being sent through the port:
MESSAGE = "I love you!"
                        # Maximum seconds to wait before the relationship fails.
SESSION_TIMEOUT = 10
                        # This speed must match the code on the arduino.
SPEED = 115200
                        # Total messages to send.
TOTAL_MESSAGES = 3

## END Programmer settings.

                    # Required communication library.
import serial
                    # Required to detect time out.
import time
                    # Required for deque.
import collections

"""
Makes a lambda function which returns true while their is time remaining.

@param seconds is the number seconds to return true.

@return a lambda function thats true while for number of seconds.
Tests:
>>>makeTimer( 1 )()
True
"""
def makeTimer( seconds ):
  startTime = time.time()
  return lambda : time.time() - startTime < seconds

def alwaysFalse( ):
  return lambda : False

# Load up the outBox with messages.
outBox = collections.deque( )
i = 0
while i < TOTAL_MESSAGES:
  outBox.append( ":t" + str(i) + "/" + str( 300 + i ) + ";" )
  i = i + 1

# Start the timer now!
startTime = time.time()
sessionTimer = makeTimer( SESSION_TIMEOUT )

foundResponse = False

# Open the port to the arduino.
with serial.Serial( port = PORT, baudrate = SPEED) as ser:

	# Avoid race condition
	time.sleep(2)
		            # Necessary initial value.
	byte = '+'
		            # What the PC sends and expects back.
	pcByte = 'H'
		            # Wait 100 ms seconds while reading
	#ser.timeout = 0.1

	print "Greeting arduino..."

	# Make contact.
	# Keep talking and listening until the Arduino
	#  answers with the same byte.
	while byte != pcByte and sessionTimer():
	  ser.write( pcByte )
	  print( "PC says: " + pcByte )
	  time.sleep( 0.300 )
	  if ser.inWaiting() > 0:
		  byte = ser.read()
		  print( "Arduino says: " + byte )

	if sessionTimer():
		ser.flushOutput()
		while ser.inWaiting() > 0:
		  ser.flushInput()
		print( "Made contact!" )
		print "Sending motor request..."
		ser.write( ":123S;" )
		ser.write( ":123Z;" )
	else:
		print "Could not make contact with arduino."

	while sessionTimer():
		if ser.inWaiting() > 0:
			print ser.read()
			foundResponse = True
if foundResponse:
	print "Received a message from Arduino!"
else:
	print "No response from Arduino"
