
#This is the skeletal structure of the main loop

from robotbasics import *
import pygame
import GUI
import landmark
import modes
import messenger

"""=================CREATE WORLD====================================="""

state = State()
state.mode = Pathfind()

landmarklist = list()
landmarklist.append(landmarks)

loglist = list()
loglist.append(logs)

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
gui.takeTerrain(landmarkList)

"""===============MAIN LOOP=========================================="""
running = True

while running == True:
    for event in pygame.event.get():
        if event.type==QUIT:
            pygame.quit()
            sys.exit()    
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                for frame in gui.frameList:
                    frame.feelClickDown(pygame.mouse.get_pos())
        if event.type == MOUSEBUTTONUP:
            if event.button == 1:
                for frame in gui.rameList:
                    frame.feelClickUp(pygame.mouse.get_pos())
            if event.button == 2:
                for frame in gui.frameList:
                    frame.feelMiddleClick()

    mode.act(state)
    gui.takeState(state)
