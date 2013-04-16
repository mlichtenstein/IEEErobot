
#   A class for objects useful to making a nice GUI
import sys
sys.path.append("..")
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
    def feelMiddleClick(self, screen_pos):
        if self.rect.collidepoint(screen_pos):
            pos = (screen_pos[0] - self.origin[0], screen_pos[1] - self.origin[1])
            self.processMiddleClick()
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
    def takeState(self, state):
        return state
    def takeMode(self, mode):
        return mode
                
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
    drawList = [EmptyDrawable()]
    mode = None
    def optionsWindow(self):
        #put a dialog to change the active state of the drawables here
        pass
    def takeState(self, state):
        self.state = state
        return state
    def takeMode(self, mode):
        self.mode = mode
        return mode
    def takeWorld(self, logList, landmarkList): #DEPRECATED -- delete this when you're in the mood for a bughunt
        self.logList = logList
        self.landmarkList = landmarkList
    def addObj(self,objList):
        for obj in objList:
            self.drawList.append(Drawable(obj))
    def draw(self):
        for drawable in self.drawList:
            if drawable.active == True:
                drawable.draw(self, self.state)
    def processMiddleClick(self):
        activeList = list()
        nameList = list()
        for drawable in self.drawList:
            nameList.append(drawable.name)
        import easygui
        makeActiveList = easygui.multchoicebox(msg="Select which world objects you'd like to be visible",
                title='View options:',
                choices=(nameList))
        if makeActiveList != None:
            for drawable in self.drawList:
                drawable.active = False
                for target in makeActiveList:
                    if target == drawable.name:
                        drawable.active = True 

"""==================================SPECIFIC VIEWS================================"""

class BoardView(View):
    """
    BoardView shows a
    birds-eye map of the board in the board's frame of reference.
    """
    def setup(self):
        import world
        self.robot = Robot((255,255,255))
        self.logSet = LogSet(world.World().logList,(139,105,20) )
        self.landmarkSet = LandmarkSet(world.World().landmarkList,(162,68,3))
        self.hypobotSet = HypobotSet((0,255,0))
        self.graphImage = GraphImage((0,0,255))
        #the bottom of the list appears on top
        self.drawList = [   self.hypobotSet,
                            self.graphImage,
                            self.logSet,
                            self.landmarkSet , self.robot]

class RangeView(View):
    """
    RangeView shows the results of a scan in the bot's frame of
    reference.
    """
    def setup(self):
        import world
        self.robot = RangeRobot((255,255,255))
        self.IRs = IRranges((255,0,0))
        self.USs = USranges((122,0,255))
        self.hIRs = hypoIRranges((122,0,0))
        self.drawList = [self.hIRs, self.robot,self.USs, self.IRs]

"""=============================ACCOUTREMENTS====================================="""

class StatusBanner(Frame):
    """
    this frame is a long horizontal bar that displays crucial info about
    the bot's state:  It's current mode, the pucks it still wants to
    collect, and the run time.
    """
    def setup(self):
        self.font = pygame.font.Font(None, 26)
        self.string = [""]*3
        self.startTime = -1
    def takeState(self, state):
        import time
        ti = time.time() - state.startTime
        self.modifyStrings(state.mode, state.remainingPucks, ti)
        return state
    def draw(self):
        self.surface.fill(0x07BB07)
        UpperLeft = [0,250, 800]
        for i in range(0,3):
            tempSurface = self.font.render(self.string[i], True, (0,0,0))
            tempUL = (UpperLeft[i],0)
            self.surface.blit(tempSurface,tempUL)
    def modifyStrings(self, mode, pucksRemaining, time):
        if mode == None:
            self.string[0] = "MODE: NONE"
        else:
            self.string[0] = "MODE: " + mode
        self.string[1] = "PUCKS REMAINING: "+str(pucksRemaining)
        self.string[2] = "TIME: " + str(time)

"""=========================CONTROLS============================================"""

class PauseButton(Frame):
    def setup(self):
        self.paused=False
        self.font = pygame.font.Font(None, 26)
    def feelClickDown(self, screen_pos):
        self.paused = not self.paused
    def takeState(self, state):
        state.paused = self.paused
        return state
    def draw(self):
        if self.paused == False:
            self.surface.fill((0,255,0))
            tempSurface = self.font.render("PAUSE", True, (0,0,0))
        else:
            self.surface.fill((255,0,0))
            tempSurface = self.font.render("UNPAUSE", True, (0,0,0))
        tempUL = (10,10)
        self.surface.blit(tempSurface,tempUL)

"""==========================GUI CLASS==========================================="""

class GUI:
    frameList = list()
    prevMode = None
    def __init__( self, pygame, screen):
        self.pygame = pygame
        self.screen = screen
        self.boardView = BoardView(pygame, screen, 10, 60, 485, 485)
        self.statusBanner = StatusBanner(pygame, screen, 10, 10, 980, 40)
        self.modeView = View(pygame,screen,560, 60, 00,000) #emptyFrame for now
        #self.modeView = RangeView(self.pygame, self.screen, 560, 60, 540,540)
        self.pauseButton = PauseButton(pygame, screen, 10, 630, 100, 100)
        self.frameList = [  self.boardView,
                            self.statusBanner,
                            self.modeView ,
                            self.pauseButton]
    def takeState(self, state):
        #this block shifts the modeView (or it should)
        if self.prevMode != state.mode:
            if state.mode == "Localize":
                self.frameList.remove(self.modeView)
                self.modeView = RangeView(self.pygame, 
                        self.screen, 505, 60, 485,485)
                self.frameList.append(self.modeView)
            if state.mode == "Pathfind":
                #self.modeFrame = pathFindView# if we want this
                pass
            self.prevMode = state.mode                
        for frame in self.frameList:
            frame.takeState(state)
        return state
    def takeMode(self,mode):
        self.mode = mode
        for frame in self.frameList:
            frame.takeMode(mode)
    def update(self,screen):
        for frame in self.frameList:
            frame.update(screen)


"""============================TEST ZONE======================================="""
        
if __name__ == "__main__":
    import time 
    print "Hello World"
    H = 700
    W = 1100
    textHeight = 18

    state = State()
    state.hypobotCloud.appendBlanket(4,45)
    
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
                        state.pause()
                        print("processing middle click...")
                        frame.processMiddleClick()
                        state.unpause()
                        
        gui.takeState(state)
        gui.update(screen)
        pygame.display.update()

        state.pose = Pose(state.pose.x+0.01,state.pose.y+0.01,state.pose.theta+0.1)
        time.sleep(0.1)
        
        #runNum -= 1
