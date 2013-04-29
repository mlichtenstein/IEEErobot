"""
A library that tells GUI how to draw things.  Each drawable is a thing
you might want to draw on a view.  Note that drawables are meant for
specific views, so using a rangeView drawable on boardView will draw, but
it won't draw what you want.
"""

import math
import pygame
import localize
import world

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
    def __init__(self, color=None, alpha = 255, default=None):
        self.color=(255,255,255)
        self.alpha = alpha
        if color is None:
            import random
            self.color = (int(random.random()*256),
                            int(random.random()*256),
                            int(random.random()*256))
        else:
            self.color = color
        if default!=None:
            self.active = default
        else:
            self.active = True
    def draw(self, view, state): #define in subclasses
        pass

def drawRange(surface, color, origin_x, origin_y, theta, startDist, endDist):
    #takes theta in units of degrees
    #all units in pixels
    start_x = origin_x + startDist*math.cos(theta*math.pi/180)
    start_y = origin_y - startDist*math.sin(theta*math.pi/180)
    end_x   = origin_x + endDist*math.cos(theta*math.pi/180)
    end_y   = origin_y - endDist*math.sin(theta*math.pi/180)
    pygame.draw.line(surface, color, (start_x,start_y), (end_x, end_y))

def drawRangeTangent(surface, color, origin_x, origin_y, theta, rDist, tanDist):
    #takes theta in units of degrees
    #all units in pixels
    mid_x   = origin_x + rDist*math.cos(theta*math.pi/180)
    mid_y   = origin_y - rDist*math.sin(theta*math.pi/180)
    start_x = mid_x - tanDist/2*math.sin(theta*math.pi/180)
    start_y = mid_y - tanDist/2*math.cos(theta*math.pi/180)
    end_x = mid_x + tanDist/2*math.sin(theta*math.pi/180)
    end_y = mid_y + tanDist/2*math.cos(theta*math.pi/180)
    pygame.draw.line(surface, color, (start_x,start_y), (end_x, end_y))

"""=====================MISC DRAWABLES=============================="""

class EmptyDrawable(Drawable):  #useful for empty views
    name = "Nothing to draw..."
    def draw(self, view, state):
        pass

class TestDrawable(Drawable): #Just draws a random color
    name = "Test Color"
    def draw(self,view,state):
        import random
        view.surface.fill((int(random.random()*256),
                          int(random.random()*256),int(random.random()*256)))

"""=======================DRAWABLES FOR BOARDVIEW==================="""
#dsd
"""since boardview is the most important, boardView drawables
don't get names referring them to boardView"""

class Robot(Drawable):
    name = "Robot"
    def draw(self, view, state):
        self.drawPose(view, state.pose)
    def drawPose(self,view, pose):
        CC = view.CC
        tempSurface = pygame.Surface((view.width, view.height))
        #the center of the robot in view's pixel coords
        x = pose.x * CC
        y = pose.y * CC
        # first draw the square frame of the robot
        robotWidth = 1
        s = view.CC*robotWidth/2
        xa = s*math.cos(pose.theta*math.pi/180)
        ya = s*math.sin(pose.theta*math.pi/180)
        xb = s*math.sin(pose.theta*math.pi/180)
        yb = s*math.cos(pose.theta*math.pi/180)
        pygame.draw.polygon(tempSurface, self.color,
                ((x-xa+xb,y+ya+yb),
                (x-xa-xb,y+ya-yb),
                (x+xa-xb,y-ya-yb),
                (x+xa+xb,y-ya+yb)), 2)
        #and draw a line for the heading:
        pygame.draw.line(tempSurface, self.color, (x,y),(x+2*xa,y-2*ya),2)
        #finally blit it:
        tempSurface.set_alpha(self.alpha)
        tempSurface.set_colorkey((0,0,0))
        view.surface.blit(tempSurface, (0,0)) #THIS CAN BE SPED UP BY BLITTING A RECTANGLE

class Wheels(Drawable):
    name = "Wheels"
    def draw(self, view, state):
        pass #nah drawing wheels is a pain

class HypobotSet(Drawable):
    name = "Hypobots"
    def draw(self, view, state):
        if state.hypobotCloud.hypobotList != list():
            peakWeight = state.hypobotCloud.peakWeight()
        for hypobot in state.hypobotCloud.hypobotList:
            import robotbasics
            alpha = int(50 + 206*hypobot.weight/peakWeight)
            pose = robotbasics.Pose(hypobot.pose.x,hypobot.pose.y,hypobot.pose.theta)
            Robot(self.color,alpha).drawPose(view,hypobot.pose)

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
            pt0=(int((log[0]+delX)*view.CC), int((log[1]+delY)*view.CC))
            pt1=(int((log[0]-delX)*view.CC), int((log[1]-delY)*view.CC))
            pt2=(int((log[2]-delX)*view.CC), int((log[3]-delY)*view.CC))
            pt3=(int((log[2]+delX)*view.CC), int((log[3]+delY)*view.CC))
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
        import world
        side = int(world.World().treeSide * view.CC)
        radius = int(world.World().rockRadius * view.CC)
        for landmark in self.landmarkList:
            x = int(landmark.x * view.CC)
            y = int(landmark.y * view.CC)
            if landmark.landmarkType == "TREE":
                rect = (x - side/2, y-side/2, side, side)
                pygame.draw.rect(view.surface, self.color, rect)
            if landmark.landmarkType == "ROCK":
                pygame.draw.circle(view.surface, self.color,
                        (x,y), radius)

class GraphImage(Drawable):
    name = "Nodes and Links"
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
    def draw(self, view, state):
        if view.mode != None:
            for node in view.mode.graph.nodes:
                #draw the nodes:
                x = node.X*view.CC/120
                y = node.Y*view.CC/120
                radius = node.radius*view.CC/120
                pygame.draw.circle(view.surface, self.color,(x,y), radius,1)
            for link in view.mode.graph.links:
                #draw the links:
                x1 = link.node1.X*view.CC/120
                y1 = link.node1.Y*view.CC/120
                x2 = link.node2.X*view.CC/120
                y2 = link.node2.Y*view.CC/120
                pygame.draw.line(view.surface, self.color, (x1,y1),(x2,y2))
                #draw departure and arrival angles:
                #departure first:
                edg = 1.0/4
                depX1 = (1-edg)*x1 + edg*x2
                depY1 = (1-edg)*y1 + edg*y2
                ariX1 = (1-edg)*x2 + edg*x1
                ariY1 = (1-edg)*y2 + edg*y1
                depRect = pygame.Rect((depX1-1,depY1-1),(3,3))
                ariRect = pygame.Rect((ariX1-1,ariY1-1),(3,3))
                pygame.draw.rect(view.surface,self.color,depRect)
                pygame.draw.rect(view.surface,self.color,ariRect)

                depX2 = depX1 + 20*math.cos(math.pi/180 * float(link.node1direction))
                depY2 = depY1 + 20*math.sin(math.pi/180 * float(link.node1direction))
                ariX2 = ariX1 + 20*math.cos(math.pi/180 * float(link.node2direction))
                ariY2 = ariY1 + 20*math.sin(math.pi/180 * float(link.node2direction))

                pygame.draw.line(view.surface, self.color, (depX1,depY1),(depX2,depY2))
                pygame.draw.line(view.surface, self.color, (ariX1,ariY1),(ariX2,ariY2))



"""====================DRAWABLES FOR RANGEVIEW======================"""
"""Drawables for the RangeView class"""

class RangeRobot(Drawable):
    name = "Robot"
    def draw(self, view, state):
        import world
        eyeList = world.World().eyeList
        #create center:
        x0 = 4*view.CC
        y0 = 4*view.CC
        #draw robot body:
        side = world.World().robotSide * view.CC
        body = pygame.Rect(0,0, side, side)
        body.center = (x0,y0)
        pygame.draw.rect(view.surface, self.color, body, 1)
        #draw eyes:
        for eye in eyeList:
            x_eye=int(x0 + eye.x_offset*view.CC)
            y_eye=int(y0 + eye.y_offset*view.CC)
            pygame.draw.circle(view.surface, self.color,(x_eye,y_eye),10,1)
        #number the eyes:
        font = pygame.font.Font(None, 18)
        for eye in eyeList:
            x_numeral=int(x0 + eye.x_offset*view.CC/2-7)
            y_numeral=int(y0 + eye.y_offset*view.CC/2-7)
            tempSurface = font.render(str(eye.eyeNum), True, eye.color)
            view.surface.blit(tempSurface,(x_numeral,y_numeral))
        #and draw a line for the heading:
        pygame.draw.line(view.surface, self.color, (x0,y0),(x0+side, y0))

class IRranges(Drawable): 
    name = "IR ranges"
    def draw(self, view, state):
        x0 = 4*view.CC
        y0 = 4*view.CC
        for eye in state.eyeList:
            import settings
            x_eye=int(x0 + eye.x_offset*view.CC)
            y_eye=int(y0 + eye.y_offset*view.CC)
            for i in range(0,settings.SCAN_DATA_POINTS):
                theta = eye.thetaList[i]
                IR = eye.IR[i] / 3
                drawRange(view.surface, self.color, x_eye,y_eye,theta,10,IR)

class hypoIRranges(Drawable):
    name = "Best Guess IR ranges"
    def draw(self, view, state):
        bestGuessHbot = localize.Hypobot(state.pose.x,
                                        state.pose.y,
                                        state.pose.theta)
        bestGuessHbot.generateEyeData(world.World().landmarkList)
        x0 = 4*view.CC
        y0 = 4*view.CC
        for eye in bestGuessHbot.localEyeList:
            import settings
            x_eye=int(x0 + eye.x_offset*view.CC)
            y_eye=int(y0 + eye.y_offset*view.CC)
            for i in range(0,settings.SCAN_DATA_POINTS):
                theta = eye.thetaList[i]
                IR = eye.IR[i] / 3
                drawRange(view.surface, self.color, x_eye,y_eye,theta+.5,10,IR)

class USranges(Drawable):
    name = "US ranges"
    def draw(self,view,state):
        x0 = 4*view.CC
        y0 = 4*view.CC
        for eye in state.eyeList:
            import settings
            x_eye=int(x0 + eye.x_offset*view.CC)
            y_eye=int(y0 + eye.y_offset*view.CC)
            for i in range(0,settings.SCAN_DATA_POINTS):
                if eye.US[i]!= 0:
                    theta = eye.thetaList[i]
                    US = eye.US[i]*view.CC
                    drawRangeTangent(view.surface, self.color,
                            x_eye,y_eye,theta,US,1*view.CC)

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
