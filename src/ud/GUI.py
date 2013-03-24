
#   A class for objects useful to making a nice GUI

import pygame
from pygame import *
from robotbasics import *
import math
import easygui as eg
from draw import *

# a class to manage frames:

class Frame:
    """
    An object of this class is a rectangle on a pygame screen.
    This rectangle can tell if it has been clicked, so children of this
    class make good simple buttons.  Also, the click is translated (or
    "felt") as coordinates with respect to the upper left corner of the
    frame, so you can use it to hold a map and enter map coordinates.
        
        Params:
            same as a pygame rectangle.
    """    
    def __init__(self, pygame, screen, x_origin, y_origin, width, height):
        pygame=pygame
        screen=screen
        self.origin = (x_origin,y_origin)
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x_origin, y_origin, width, height)
        #^the rectangle the frame occupies in the screen
        self.surface = pygame.Surface((width, height))
        self.CC = width/8 #coordconversion transforms feet to pixels
        self.setup() #used to add to init procedures if you want
    def update(self,screen):
        self.surface.fill(0x000000)
        self.draw()
        screen.blit(self.surface, self.rect)
    def feelClickDown(self, screen_pos):
        if self.rect.collidepoint(screen_pos):
            pos = (screen_pos[0] - self.origin[0], screen_pos[1] - self.origin[1])
            self.processClickDown(pos)
    def feelClickUp(self, screen_pos):
        if self.rect.collidepoint(screen_pos):
            pos = (screen_pos[0] - self.origin[0], screen_pos[1] - self.origin[1])
            self.processClickUp(pos)     
    def draw(self):  #this is meant to be overwritten by child classes
        pass
    def processClickDown(self, pos):  #this is meant to be overwritten by child classes
        pass
    def processClickUp(self, pos):  #this is meant to be overwritten by child classes
        pass
    def processMiddleClick(self):
        pass
    def setup(self):
        pass
                
class Button(Frame): 
    down = False
    downColor = 0x10B62C
    upColor = 0x90EE90
    background = 0x90EE90
    text = "[set text]"
    textColor = (00,00,00,55)
    def __init__(self, pygame, screen, x_origin, y_origin, width, height, text, font, startState):        #the corners on the big canvas
        pygame=pygame
        screen=screen
        self.font=font
        self.origin = (x_origin,y_origin)
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x_origin, y_origin, width, height) #the rectangle the frame occupies in the screen
        self.surface = pygame.Surface((width, height))
        self.text = text
        self.down = startState
    def processClickDown(self, screen_pos):
        self.down = not self.down
    def draw(self):
        if self.down: 
            self.background=self.downColor
        else: 
            self.background=self.upColor
        self.surface.fill(self.background)
        self.drawText()
    def drawText(self):
        tempSurface = self.font.render(self.text, True, self.textColor)
        tempUL = ((self.width-tempSurface.get_width())/2,(self.height-tempSurface.get_height())/2)
        self.surface.blit(tempSurface,tempUL)

class View(Frame): # a frame for representations of physical data (boardView, botView)
    state = State()
    selectedHypobot=0
    drawList = list()
    coordConversion = 540/8
    def optionsWindow(self):
        #put a dialog to change the active state of the drawables here
        pass
    def takeState(self, state):
        self.state = state
    def takeWorld(self, logList, landmarkList):
        self.logList = logList
        self.landmarkList = landmarkList
    def addObj(self,objList):
        for obj in objList:
            self.drawList.append(Drawable(obj))
    def draw(self):
        for drawable in self.drawList:
            if drawable.active == True:
                drawable.draw(self, self.state)

class BoardView(View):
    def setup(self):
        import world
        self.robot = Robot()
        self.logSet = LogSet(world.World().logList)
        self.drawList = [self.robot, self.logSet]

class GUI:
    frameList = list()
    def __init__( self, pygame, screen):
        self.boardView = BoardView(pygame, screen, 10, 10, 540, 540)
        self.frameList.append(self.boardView)
    def takeState(self, state):
        for frame in self.frameList:
            frame.takeState(state)
    def update(self,screen):
        for frame in self.frameList:
            frame.update(screen)
        
if __name__ == "__main__":
    import time 
    print "Hello World"
    H = 700
    W = 1100
    textHeight = 18

    state = State()
    
    pygame.init()
    pygame.font.init()
    Font = pygame.font.Font(None, textHeight)
    screen=pygame.display.set_mode((W,H),0,32)
    screen.fill((127,127,127))
    gui = GUI(pygame,screen)
    #set up frames:
    #BoardView = boardView(pygame, screen, 5, 30, 540, 540, LandmarkList, LogList, EyeList)
    #BoardView.takeBestGuessBot(BestGuessBot)
    #buttons for BoardView:
    """
    boardView=BoardView(pygame, screen, 10, 10, 540, 540)
    """

    runNum = 0

    
    """----------------MAIN LOOP -------------------"""
    while runNum >= 0:
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
                    for frame in gui.frameList:
                        frame.feelClickUp(pygame.mouse.get_pos())
                if event.button == 2:
                    for frame in gui.frameList:
                        frame.feelMiddleClick()
                        
        gui.takeState(state)
        gui.update(screen)
        pygame.display.update()

        state.pose = Pose(state.pose.x+0.01,state.pose.y+0.01,state.pose.theta+0.1)
        time.sleep(0.1)
        
        #runNum -= 1
