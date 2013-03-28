import pygame, sys, math, edit, random, pickle, easygui
from pygame.locals import *
import graph as g

if __name__ == "__main__":
    LOAD_FILE = easygui.fileopenbox(msg=None, title=None, default=None)

def loadFile( name ) :
    try:
        f = open( name, "rb" )
        return pickle.load( f )
    except:
        print " no file selected "

def writeFile( name ):
    try:
        f = open( name, "wb" )
        pickle.dump( graph, f )
    except:
        print " no file selected "

if __name__ == "__main__":
    try:
        graph = loadFile( LOAD_FILE )
    except (IOError, ImportError,RuntimeError, TypeError, NameError, AttributeError) as e:
        #import traceback
        print e
        #traceback.print_stack()
    if graph == None:
        graph = g.Graph()
    pucks = random.sample(range(1,17),6)
    dummy = graph.addNode(-1000,-1000)
    pygame.init()
    screen=pygame.display.set_mode((960,960),0,32)
    pose = (0,0,0)
    drawFlag = 1
    botPose = g.Pose()

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
        x = (p-1)%4*240+120
        y = (p-1)/4*240+120
        pygame.draw.circle ( screen, (90,175,70), (x,y), 15)

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
            pygame.draw.line(screen,(0,0,200), (node.X,node.Y),(node.X+60*math.cos(node.theta*math.pi/180),node.Y-60*math.sin(node.theta*math.pi/180)),4)
            pygame.draw.circle(screen, (0,0,200), (int(node.X+100*math.cos(node.theta*math.pi/180)),int(node.Y-100*math.sin(node.theta*math.pi/180))), 40, 4)

        pygame.draw.circle(screen,(red,green,blue),(node.X,node.Y), node.radius)
        pygame.draw.circle(screen,(0,0,0),(node.X,node.Y), node.radius,1)

    for link in graph.links:
		#draw links
        pygame.draw.line( screen, (link.red,link.green,link.blue), (link.node1.X,link.node1.Y),(link.node2.X,link.node2.Y),2)
		#draw link click location as a small circle
        pygame.draw.circle ( screen, (link.red/2,link.green/2,link.blue/2), ((link.node1.X+link.node2.X)/2,(link.node1.Y+link.node2.Y)/2), 6, 2)
                            #draw link directionality vectors (two of them)

        temp1=int(link.node1.X+12*math.cos(math.pi/180*float(link.node1direction)))
        temp2=int(link.node1.Y-12*math.sin(math.pi/180*float(link.node1direction)))
        temp3=int(link.node2.X+12*math.cos(math.pi/180*float(link.node2direction)))
        temp4=int(link.node2.Y-12*math.sin(math.pi/180*float(link.node2direction)))
        
        pygame.draw.line( screen, (link.red/2,link.green/2,link.blue/2), (link.node1.X,link.node1.Y), (temp1, temp2), 4)
        pygame.draw.line( screen, (link.red/2,link.green/2,link.blue/2), (link.node2.X,link.node2.Y), (temp3, temp4), 4)
            

def drawAll():
    screen.lock()
    drawObjects()
    drawPucks()
    drawGraph()
    screen.unlock()
    pygame.display.update()

def makeTimer( seconds ):
    import time
    startTime = time.time()
    return lambda : time.time() - startTime < seconds

def drawLine(x1,y1,x2,y2): #draws a thick red line
    pygame.draw.line(screen, (255,0,0), (x1,y1),(x2,y2),3)
    pygame.display.update()


def scootToNearestNode((X,Y, theta)): #returns the node
    nearestNode = whatNode((X,Y))[0]
    distance = whatNode((X,Y))[1]
    nodeTheta = 180/math.pi* math.atan2(nearestNode.Y-Y,nearestNode.X-X)

    angle = theta - nodeTheta
    if distance > nearestNode.radius: #start by fixing any corretions
        print angle
        print distance
        #distance = math.hypot(X,Y,nearestNode.X,nearestNode.Y)
        #
        #scoot(distance, angle)#                   <======================== out to arduino
        #don't localize here (but.. maybe?)
        #update bot pose once correction is done
        ''' this code  is for the simulation'''
        drawLine(X,Y,nearestNode.X,nearestNode.Y)
        botPose.X, botPose.Y = nearestNode.X, nearestNode.Y
        drawBot(X,Y,theta)
    return nearestNode
DEBUG = False

def explorePath( allLinks, roots, startingNode ):
    """
    Description:
    The method tries to find the shortest path to a node.

    Parameters:
    allLinks -- is a list of all links in the graph.
    roots -- is a list of roots.
    startingNode -- is the base of the path.

    Return:
    A tuple of the path and the distance.

    Example:
    >>> 
    """
    currentNode = startingNode
    previous = roots[-1]
    result = []
    distance = 0
    while True:
        if DEBUG:
            print "previous: ", previous
            print "currentNode: ", currentNode
        result.append( currentNode )
        # Done once we have the puck.
        if currentNode.puck != -1:
            if DEBUG:
                print "Puck"
            break
        relatedLinks = findLinksWithNode( allLinks, currentNode )
        forwardLinks = [] 
        # No matches. There should be at least one link that matches.
        if len( relatedLinks ) == 0:
            raise Exception( "Cannot find starting node." )
        else:
            for link in relatedLinks:
                # Access the oposite node from currentNode.
                otherNode = getOtherNode( link, currentNode )
                needToExplore = True
                # The link goes backwards.
                if otherNode == previous:
                    needToExplore = False
                # Ignore links to intersections previously explored.
                if needToExplore:
                    for root in roots:
                        if otherNode == root:
                            needToExplore = False
                            break
                # Include only forward going links.
                if needToExplore:
                    forwardLinks.append( link )
        # No forward links.
        if len( forwardLinks ) == 0:
            if DEBUG:
                print "Deadend"
            return None
        # One forward link. Proceed forward.
        elif len( forwardLinks ) == 1:
            if DEBUG:
                print "One forward link"
            # Access the oposite node from currentNode.
            distance = distance + forwardLinks[0].length
            nextNode = getOtherNode( forwardLinks[0], currentNode )
            previous = currentNode
            currentNode = nextNode 
        # Multiple forward links. Divide and conquer.
        else:
            # For each possible branch, launch an explorer. The explorer will
            #  return the path and the distance. Next, append the branch with
            #  the shortest path.
            if DEBUG:
                print "Multiple forward links"
            minBranch = None
            minLink = None
            for link in forwardLinks:
                if DEBUG:
                    print "link: ", link
                otherNode = getOtherNode( link, currentNode )
                rootsCopy = roots[:]
                rootsCopy.append( currentNode )
                branch = explorePath( allLinks, rootsCopy, otherNode )
                if DEBUG:
                    print "minBranch: ", minBranch
                    print "Branch: ", branch
                # Select the shortest branch only.
                if branch != None and ( minBranch == None or \
                branch[1] < minBranch[1] ):
                    minBranch = branch
                    minLink = link
                    if DEBUG:
                        print "minBranch set"
            if minLink != None:
                result = result + minBranch[0]
                distance = distance + minLink.length + minBranch[1]
            else:
                return None
            break
    return ( result, distance )

def findPath( graph, startingNode ):
    """
    Return:
    The path.
    """
    pathInfo = explorePath( graph.links, [startingNode], startingNode )
    if pathInfo == None:
        raise Exception( "Puck not found" )
    print "Distance: ", pathInfo[1]
    return pathInfo[0]
def findLinksWithNode( links, node ):
    result = []
    for link in links:
        if link.node1 == node or link.node2 == node:
            result.append( link )
    return result

def getOtherNode( link, node ):
    if link.node1 == node:
        return link.node2
    else:
        return link.node1
    
# By default accept all mouse up events.
ignoreNextMouseUpEvent = lambda: False
while __name__ == "__main__":
    for event in pygame.event.get():
        if event.type == QUIT:
            LOAD_FILE = easygui.filesavebox(msg="Save File", title=None, default=None)
            writeFile( LOAD_FILE )
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
            
            clickedLink = False
            for link in graph.links:
                if math.hypot(posDown[0]-(link.node1.X+link.node2.X)/2, posDown[1]-(link.node1.Y+link.node2.Y)/2)<6:
                    clickedLink = True
                    

            #clicked on link - so edit link
            if clickedLink:
                clickedLink=False
                link.update()
                while 1:
                    if edit.editLink(link):
                        drawAll()
                        link.update()
                    else:
                        link.update()
                        break
                # Ignore mouse clicks for the next 250 ms
                ignoreNextMouseUpEvent = makeTimer(0.250)
            #clicked in execute box
            elif posDown[0]>940 and posDown[1]<20:
                drawFlag=0
                while 1:
                    if edit.editBot(botPose):
                        drawAll()
                    else:
                        thenode = scootToNearestNode((botPose.X,botPose.Y, botPose.theta))
                        try:
                            print "Before findpath"
                            path = findPath( graph, thenode )
                            print "After findpath"
                            print path
                            
                            lastPath = path[0]
                            for i in path:
                                print i
                                drawLine(lastPath.X,lastPath.Y,i.X,i.Y)
                                lastPath = i
                        except Exception as e:
                            print "Error: ", e
                        break
                # Ignore mouse clicks for the next 250 ms
                ignoreNextMouseUpEvent = makeTimer(0.250)
            
            elif whatNode(posDown)[1] <= downNode.radius:   #if click was inside a node
                print "what node is returning " + str(whatNode(posDown)[0])
                if whatNode(posUp)[1] <= upNode.radius:  #and  unclick was inside a node
                    if downNode==upNode:  #and those were the same nodes
                        right_mouse=pygame.mouse.get_pressed()

                        print right_mouse
                        if right_mouse[2] == 1:#and right mouse button was down
                                drawFlag=0
                                for link in graph.links:
                                    link.update()
                                while 1:
                                    if edit.editNode(upNode):
                                        drawAll()
                                        for link in graph.links:
                                            link.update()
                                    else:
                                        link.update()
                                        break
                                # Ignore mouse clicks for the next 250 ms
                                ignoreNextMouseUpEvent = makeTimer(0.250)
                        else:
                                graph.removeNode(whatNode(posDown)[0])  #remove that node
                    else: # but if they were two different nodes
                        red=random.randint(0,255)
                        green=random.randint(0,255)
                        blue=random.randint(0,255)
                        graph.addLink( downNode, upNode, (red,green,blue) )#then make a link between

                else:#clicked in a node, and dragged into space
                        downNode.X = posUp[0]
                        downNode.Y = posUp[1] #drag node
                        for link in graph.links:#reclaculate the length of links after a drag
                            if downNode == (link.node1 or link.node2):
                                link.update()
#add a distance calculation

            else: # clicked not on a node
                if clickTravel <= downNode.radius: #clicked and didnt drag
                        graph.addNode(posDown[0], posDown[1])#add a node
                elif clickTravel > downNode.radius: #clicked and dragged
                        pose = ( posDown[0], posDown[1], 180/math.pi*math.atan2((posDown[0]-posUp[0]),(posDown[1]-posUp[1])) ) #drop bot on this node

    if drawFlag ==1:
        drawAll()
        drawFlag=0

    
