import pyarm
import serial
import messenger


ard = messenger.Messenger(messenger.SerialPort())
ard.sendMessage('G', '90,0,90')
leString = pyarm.grab()
ard.sendMessage('G', leString)
print leString

