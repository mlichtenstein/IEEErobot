import pyarm
import messenger

ard = messenger.Messenger(messenger.SerialPort())
ard.sendMessage('G', '0,0,0')
leString = pyarm.grab()
ard.sendMessage('G', leString)
print leString

