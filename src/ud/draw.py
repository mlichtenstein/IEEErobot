import math
import pygame

class Drawable:
    """
    Drawables are things that frames can draw.  A frame owns one as an
    attribute.  The "Active" variable is used to make it invisible.

    The draw function should always take view and state as an argument.
    state is unimportant for static drawables, but it keeps the notation
    consistent

    The various objects that drawables can be are below.  Later,
    they should be moved to their own library. 
    """
    active = True;
    color=(255,255,255)
    name = "Give me a name!"
    def __init__(self, color=None, default=None):
        self.color=(255,255,255)
        if color is None:
            import random
            self.color = (int(random.random()*256),
                            int(random.random()*256),
                            int(random.random()*256))
        else:
            self.color = color
        if default!=None:
            self.active = default
    def draw(self, view, state): #define in subclasses
        pass

class Robot(Drawable):
    name = "Robot"
    def draw(self, view, state):
        CC = view.CC
        #the center of the robot in view's pixel coords
        x = state.pose.x * CC
        y = state.pose.y * CC
        # first draw the square frame of the robot
        robotWidth = 1
        s = view.CC*robotWidth/2
        xa = s*math.sin(state.pose.theta)
        ya = s*math.cos(state.pose.theta)
        xb = s*math.cos(state.pose.theta)
        yb = s*math.sin(state.pose.theta)
        pygame.draw.polygon(view.surface, self.color,
                ((x-xa+xb,y+ya+yb),
                (x-xa-xb,y+ya-yb),
                (x+xa-xb,y-ya-yb),
                (x+xa+xb,y-ya+yb)), 1)
        #and draw a line for the heading:
        pygame.draw.line(view.surface, self.color, (x,y),(x-2*xa,y+2*ya)) #I THINK THIS IS WRONG
        #and draw the wheels?  MAYBE WHEN MAX IS FEELING UP FOR SOME SERIOUS LINEAR ALGEBRA :)

class Wheels(Drawable):
    name = "Wheels"
    def draw(self, view, state):
        

class LogSet(Drawable):
    name = "Logs"
    def __init__(self, logList, color=None, default=None):
        self.logList = logList
        self.color=(255,255,255)
        if color is None:
            import random
            self.color = (int(random.random()*256),
                            int(random.random()*256),
                            int(random.random()*256))
        else:
            self.color = color
        if default!=None:
            self.active = default
    def draw(self, view, state):
        for log in self.logList:  #logs are, in this context, fallen logs rather than logarithms
            delX = 1.0/12*(log[1]-log[3])/math.sqrt((log[0]-log[2])**2 + (log[3]-log[1])**2)
            delY = 1.0/12*(log[2]-log[0])/math.sqrt((log[0]-log[2])**2 + (log[3]-log[1])**2)
            pt0=(int((log[0]+delX)*view.coordConversion), int((log[1]+delY)*view.coordConversion))
            pt1=(int((log[0]-delX)*view.coordConversion), int((log[1]-delY)*view.coordConversion))
            pt2=(int((log[2]-delX)*view.coordConversion), int((log[3]-delY)*view.coordConversion))
            pt3=(int((log[2]+delX)*view.coordConversion), int((log[3]+delY)*view.coordConversion))
            pygame.draw.aalines(view.surface, self.color, True, (pt0,pt1,pt2,pt3))

class LandmarkSet(Drawable):
    name = "Landmarks"
    def __init__(self, landmarkList, color=None, default=None):
        self.landmarkList = landmarkList
        self.color=(255,255,255)
        if color is None:
            import random
            self.color = (int(random.random()*256),
                            int(random.random()*256),
                            int(random.random()*256))
        else:
            self.color = color
        if default!=None:
            self.active = default
    def draw(self, view, state):
        from world import *
        side = int(World().treeSide * view.CC)
        radius = int(World().rockRadius * view.CC)
        for landmark in self.landmarkList:
            x = int(landmark.x * view.CC)
            y = int(landmark.y * view.CC)
            if landmark.landmarkType == "TREE":
                rect = (x - side/2, y-side/2, side, side)
                pygame.draw.rect(view.surface, self.color, rect)
            if landmark.landmarkType == "ROCK":
                pygame.draw.circle(view.surface, self.color,
                        (x,y), radius)

"""====================TESTING GROUND==============================="""

if __name__ == "__main__":
    import time
    import robotbasics
    import GUI
    print "Hello World"
    H = 540
    W = 540
    textHeight = 18
    
    pygame.init()
    pygame.font.init()
    Font = pygame.font.Font(None, textHeight)
    screen=pygame.display.set_mode((W,H),0,32)
    screen.fill((0,0,0))

    testView = GUI.View(pygame, screen, 0,0, H, W)
    logList = [(2,6,6,2)]
    landmarkList = [robotbasics.Landmark(2,2,"TREE"),robotbasics.Landmark(6,6,"ROCK")]
    
    state = robotbasics.State()
    state.pose = robotbasics.Pose(4,4,30)
    testView.takeState(state)
    
    testView.drawList = [LogSet(logList),Robot(),LandmarkSet(landmarkList)]
    runNum = 0
    robot = Robot()
    
    """----------------MAIN LOOP -------------------"""
    while runNum >= 0:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()    

        testView.update(screen)
        pygame.display.update()

        time.sleep(0.1)
