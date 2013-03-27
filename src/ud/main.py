
#This is the skeletal structure of the main loop

from robotbasics import *
import pygame
import GUI
import landmark
import modes
import messenger
import world

"""=================CREATE WORLD====================================="""

#give the robot a state:
state = State()

#establish a serial connection that will persist into modes.py:
modes.Mode.messenger = messenger.Messenger(messenger.SerialPort())


robotMode = modes.ReadUSBDrive(state)


landmarkList = world.World.landmarkList
logList = world.World.logList

#load nodelist however you do that

H = 700
W = 1100
textHeight = 18

pygame.init()
pygame.font.init()
Font = pygame.font.Font(None, textHeight)
screen=pygame.display.set_mode((W,H),0,32)
screen.fill((127,127,127))

gui = GUI.GUI(pygame,screen)

"""===============MAIN LOOP=========================================="""
running = True

while running == True:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit()
            sys.exit()    
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for frame in gui.frameList:
                    frame.feelClickDown(pygame.mouse.get_pos())
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                for frame in gui.rameList:
                    frame.feelClickUp(pygame.mouse.get_pos())
            if event.button == 2:
                for frame in gui.frameList:
                    frame.processMiddleClick()

    # Tell the robot brain to take action.
    # NOTE--I modified this to make it possible to escape the .act()s
    # and return to this loop, so we can update the GUI between .act()s.
    # See my Localize class to see how that works.  --Max
    nextMode = robotMode.act(state)
    if nextMode != None:
        robotMode = nextMode
        


    print(robotMode)
    
    # Update the GUI with the current robot state
    gui.takeState(state)

    gui.update(screen)
    pygame.display.update()
