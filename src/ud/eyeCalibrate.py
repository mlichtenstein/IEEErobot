# Include the robot directory in the search path when importing modules.
import sys
sys.path.append( "robot" )

import messenger
import time

f = open("eyeCalibrationData/calibData"+str(time.time()), 'w')

messenger = messenger.Messenger(messenger.SerialPort())
inches = 3 #initial inches
mescount = 0
while True:
    ch = sys.stdin.read(1)   
    if ch == "q":
        break;
    messenger.sendMessage("i")
    while not messenger.checkInBox():
        pass
    print inches
    data = messenger.getMessageTuple()[2]
    mescount +=1
    if mescount ==3:
        inches +=1
        mescount = 0

    f.write(str(inches)+","+str(data)+"\n")
f.close
print f

