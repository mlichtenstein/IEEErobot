import pygame, sys, math, edit, random, pickle
from pygame.locals import *
import graph as g



LOAD_FILE = "test"

def loadFile( name ) :
    f = open( name, "rb" )
    return pickle.load( f )
    #graph.links = pickle.load( f )

    #print graph.links[0].node1
    

     

def writeFile( name ):
    f = open( name, "wb" )
    pickle.dump( graph, f )

    #f.write( pickle.dumps( graph.links ) )
try:
    graph = loadFile( LOAD_FILE )
except (IOError, ImportError,RuntimeError, TypeError, NameError, AttributeError) as e:
    #import traceback
    print e
    #traceback.print_stack()
    graph = g.Graph()
pucks = random.sample(range(1,17),6)

dummy = graph.addNode(-1000,-1000)
pygame.init()
screen=pygame.display.set_mode((960,960),0,32)
pose = (0,0,0)
drawFlag = 1
botPose = g.Pose()

#f = open('nodeFile', 'r+') #open file for reading and writing
#graph.nodes = pickle.load( f )


#load every node from graph.nodes and every link from graph.links from a file
#use addNode



def drawObjects():
    blocks = [(235-17,607-17,34,34),(258-17,250-17,34,34),(737-17,739-17,34,34),(942-17,198-17,34,34)]

    circles = [(180,875),(498,118),(469,598)]

    logList =((0,480,360,0),\
            (368.4,19.2,480,484.8),\
            (904.8,0,600,178.8),\
            (904.8,360,600,702),\
            (955.2,672,480,230.4),\
            (2.4,720,722.4,955.2),\
            (399.6,955.2,260.4,516))

    radiusCan=33
    colorCan=(139,137,137) #RGB
    colorWood=(160,82,45) #RGB
    colorLine=(150,150,100) #RGB
    gridColor=(0,105,0) #RGB

    screen.fill((200,200,200))
    pygame.draw.rect(screen, (random.randint(0,255),random.randint(0,255),random.randint(0,255)), (940,0,960,20))
    for i in range(1,4):
        pygame.draw.line(screen,gridColor,(0,i*240),(960,i*240),1)
        pygame.draw.line(screen,gridColor,(i*240,0),(i*240,960),1)
    for block in blocks:
        pygame.draw.rect(screen, colorWood, block)
    for circle in circles:
        pygame.draw.circle(screen, colorCan, circle, radiusCan)
    for log in logList: #logs are, in this context, fallen logs rather than logarithms
        delX = 10*(log[1]-log[3])/math.sqrt((log[0]-log[2])**2 + (log[3]-log[1])**2)
        delY = 10*(log[2]-log[0])/math.sqrt((log[0]-log[2])**2 + (log[3]-log[1])**2)
        pt0=(int((log[0]+delX)), int((log[1]+delY)))
        pt1=(int((log[0]-delX)), int((log[1]-delY)))
        pt2=(int((log[2]-delX)), int((log[3]-delY)))
        pt3=(int((log[2]+delX)), int((log[3]+delY)))
        pygame.draw.aalines(screen, (0xA5,0x2A,0x2A), True, (pt0,pt1,pt2,pt3))
    drawBot(botPose.X, botPose.Y, botPose.theta)
    pygame.display.update()

def drawBot(x, y, theta):
    theta = theta * math.pi/180
    pygame.draw.polygon(screen, (245,245,245), ((x+60*math.cos(theta)-60*math.sin(theta),y-60*math.sin(theta)-60*math.cos(theta)),(x-60*math.cos(theta)-60*math.sin(theta),y+60*math.sin(theta)-60*math.cos(theta)),(x-60*math.cos(theta)+60*math.sin(theta),y+60*math.sin(theta)+60*math.cos(theta)),(x+60*math.cos(theta)+60*math.sin(theta),y-60*math.sin(theta)+60*math.cos(theta))), 1)
    pygame.draw.line(screen,(245,245,245), (x,y),(x+60*math.cos(theta),y-60*math.sin(theta)),3)
    pygame.draw.circle(screen, (255,255,255), (int(x+100*math.cos(theta)),int(y-100*math.sin(theta))), 40, 1)
    pygame.display.update()

def drawPucks():
    for p in pucks:
        x=(p-1)%4*240+120
        y=(p-1)/4*240+120
        pygame.draw.circle(screen, (90,175,70), (x,y), 15)

def whatNode((x,y)):
    nearestNode=graph.nodes[0]
    distance=960**2
    distanceLowest = 960**2

    for node in graph.nodes:
        distance = math.hypot(x-node.X,y-node.Y)
        if distance<distanceLowest:
            nearestNode=node
            distanceLowest=distance
    return (nearestNode, distanceLowest)

def drawGraph():
    for node in graph.nodes:#draw nodes
        red=0
        green = 255
        blue = 255
        if not ( node.localize == 0):
            green = 150
        if 0 <= node.puck <= 15:
            blue = 150
            pygame.draw.line(screen,(red, green, blue), (node.X,node.Y),(node.X-60*math.sin(node.theta*math.pi/180),node.Y-60*math.cos(node.theta*math.pi/180)),3)
            pygame.draw.circle(screen, (red, green, blue), (int(node.X-100*math.sin(node.theta*math.pi/180)),int(node.Y-100*math.cos(node.theta*math.pi/180))), 40, 1)

        pygame.draw.circle(screen,(red,green,blue),(node.X,node.Y), node.radius)
        pygame.draw.circle(screen,(0,0,0),(node.X,node.Y), node.radius,1)

    for link in graph.links:#draw links
        print "node1 = " + str(link.node1.X+link.node1.Y) + "    node2 = " + str(link.node2.X+link.node2.Y)
        pygame.draw.line(screen, (0,100,155), (link.node1.X,link.node1.Y),(link.node2.X,link.node2.Y),2)


def drawAll():
    screen.lock()
    drawObjects()
    drawPucks()
    drawGraph()
    screen.unlock()
    pygame.display.update()

def makeTimer( seconds ):
    """
    >>> timer = makeTimer( .1 )
    >>> timer()
    True
    """
    import time
    startTime = time.time()
    return lambda : time.time() - startTime < seconds

def drawLine(x1,y1,x2,y2):
    pygame.draw.line(screen, (random.randint(0,255),random.randint(0,255),random.randint(0,255)), (x1,y1),(x2,y2),1)
    pygame.display.update()


def pathfind():
    nearestNode = whatNode((botPose.X,botPose.Y))[0]
    distance = whatNode((botPose.X,botPose.Y))[1]
    nodeTheta = 180/math.pi* math.atan2(nearestNode.Y-botPose.Y,nearestNode.X-botPose.X)

    angle = botPose.theta - nodeTheta
    if distance > nearestNode.radius: #start by fixing any corretions
        print angle
        print distance
        #drawLine(botPose.X,botPose.Y,nearestNode.X,nearestNode.Y)

        #scoot(distance, angle)#                   <======================== out to arduino
        #rotate(theta)                             <======================== out to arduino
        #don't localize here (but.. maybe?)
        #update bot pose once correction is done
        ''' this code  is for the simulation'''
        #botPose.theta = angle
        drawLine(botPose.X,botPose.Y,nearestNode.X,nearestNode.Y)
        botPose.X, botPose.Y = nearestNode.X, nearestNode.Y
        drawBot(botPose.X,botPose.Y,botPose.theta)


# By default accept all mouse up events.
ignoreNextMouseUpEvent = lambda: False
while 1:
    for event in pygame.event.get():
        if event.type == QUIT:
            writeFile( LOAD_FILE )
            #pickle.dump(graph.nodes, f)#----------------------------------save every nodes and link
            pygame.quit()
            sys.exit()

        # Ignore mouse up events.
        if ignoreNextMouseUpEvent() and ( event.type == pygame.MOUSEBUTTONDOWN \
         or event.type == pygame.MOUSEBUTTONUP ):
            print "ignore mouse Up"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            posDown=pygame.mouse.get_pos()
            downNode=whatNode(posDown)[0]
            #note which node it is in
            drawFlag = 1

        elif event.type == pygame.MOUSEBUTTONUP:
            print "mouse Up"
            posUp = pygame.mouse.get_pos()
            upNode = whatNode(posUp)[0]
            #if in the same node, then:
            drawFlag = 1

            clickTravel = math.hypot(posDown[0]-posUp[0],posDown[1]-posUp[1])

            if posDown[0]>940 and posDown[1]<20: #clicked in drop bot box
                drawFlag=0
                while 1:
                    if edit.editBot(botPose):
                        drawAll()
                    else:
                        pathfind()
                        break
                # Ignore mouse clicks for the next 150 ms
                ignoreNextMouseUpEvent = makeTimer(0.150)

            elif whatNode(posDown)[1] <= downNode.radius:   #if click was inside a node
                print "what node is returning " + str(whatNode(posDown)[0])
                if whatNode(posUp)[1] <= upNode.radius:  #and  unclick was inside a node
                    if downNode==upNode:  #and those were the same nodes
                        right_mouse=pygame.mouse.get_pressed()

                        print right_mouse
                        if right_mouse[2] == 1:#and right mouse button was down
                                drawFlag=0
                                while 1:
                                    if edit.editNode(upNode):
                                            drawAll()
                                    else:
                                            break
                                # Ignore mouse clicks for the next 150 ms
                                ignoreNextMouseUpEvent = makeTimer(0.150)
                        else:
                                graph.removeNode(whatNode(posDown)[0])  #remove that node
                    else: # but if they were two different nodes
                        graph.addLink(downNode, upNode)#then make a link between
                else:#clicked in a node, and dragged
                        downNode.X = posUp[0]
                        downNode.Y = posUp[1] #drag node

            else: # clicked not on a node
                if clickTravel <= downNode.radius: #clicked and didnt drag
                        graph.addNode(posDown[0], posDown[1])#add a node
                elif clickTravel > downNode.radius: #clicked and dragged
                        pose = ( posDown[0], posDown[1], 180/math.pi*math.atan2((posDown[0]-posUp[0]),(posDown[1]-posUp[1])) ) #drop bot on this node

    if drawFlag ==1:
        drawAll()
        drawFlag=0

def findPath( graph, startingNode ):
    """
    Return:
    The path.
    """
    pathInfo = explorePath( graph.links, startingNode, startingNode )
    return pathInfo[0]
def explorePath( links, previous, startingNode ):
    result = []
    while True:
        links = findLinksWithNode( links, startingNode )
        # No matches.
        if len( links ) == 0:
            raise Exception( "Cannot find starting node." )
        # Explore one direction.
        elif len( links ) == 1:
            otherNode = findLinksWithNode( links[0], startingNode )
            # Reached a dead-end.
            if otherNode == previous:
                break
            result.append( startingNode )
            previous = startingNode
            startingNode = otherNode
        # Explore multiple directions
        else:
            shortestTrip = 9999999
            for link in links:
                otherNode = findLinksWithNode( links[0], startingNode )
                if otherNode != previous:
                    pathInfo = explorePath( links, startingNode, otherNode )
            break
    return result
def findLinksWithNode( links, node ):
    result = []
    for link in links:
        if link.node1 == node or link.node2 == node:
            result.append( link )
    return result
def getOtherNode( link, node ):
    if links[0].node1 == node:
        return links[0].node2
    else:
        return links[1].node1
    
