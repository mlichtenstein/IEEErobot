#import pygame, math, edit, random, pickle, easygui
#from pygame.locals import *
import math, pickle

"""
pose = (0,0,0)
pucks = random.sample(range(1,17),6) #get this from USB drive
dummy = graph.addNode(-1000,-1000)
botPose = g.Pose()
"""
name = "FinalFile"# <========================================================= File where Graph is stored
def loadFile( name ) :
    try:
        f = open( name, "rb" )
        return pickle.load( f )
    except:
        print " no file selected "

def writeFile( name, graphData ):
    try:
        f = open( name, "wb" )
        pickle.dump( graphData, f )
    except:
        print " no file selected "

"""   
try:
    f = open( name, "rb" )
    return pickle.load( f )
except:
    print " no file selected "
    
try:
        graph = loadFile( LOAD_FILE )
except (IOError, ImportError,RuntimeError, TypeError, NameError, AttributeError) as e:
    #import traceback
    print e
    #traceback.print_stack()
if graph == None:
    graph = g.Graph()
    
#eliminate grab from nodes that dont have a puck
for node in graph.nodes:
    temp = 0
    for puck in pucks:
        if node.puck == puck:
            temp = 1
    if temp ==0:
        node.puck = -1
"""
def whatNode( graph, (x,y) ):
    """"
    Gets the nearest node from the current x and y position.
    
    Parameters:
    graph -- is the graph containing links which is a list of links and nodes
     which is a list of nodes.
    (x, y) -- a tuple of a x and y coordinate. Currently, this syntax is only
     supported in Python 2.7.
    
    Returns
    The nearest node.
    """
    nearestNode=graph.nodes[0]
    distance=960**2
    distanceLowest = 960**2

    for node in graph.nodes:
        distance = math.hypot(x-node.X,y-node.Y)
        if distance<distanceLowest:
            nearestNode=node
            distanceLowest=distance
    return (nearestNode, distanceLowest)

def makeAMove((X,Y, theta)):
    """
    Description:
    The method decides what Act will come next

    Parameters:
    passed as a tuple of 3 pieces of information
    X -- the robots X position
    Y -- the robots Y position
    theta -- the robots theta orientation

    Return:
    The node it ends up on

    Example:
    >>> 
    """
    #pull IMU and average into (or replace) theta here
    return theGuts.whatNode( graph,(X,Y))[0]

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
        result.append( currentNode )
        if currentNode.puck != -1:
            # puck found!
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
            if minLink == None:
                return None
            result = result + minBranch[0]
            distance = distance + minLink.length + minBranch[1]
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
    path = pathInfo[0]
    firstNode = path[0]
    secondNode = path[1]
    links = findLinksWithNode( graph.links, firstNode )
    for link in links:
        otherNode = getOtherNode( link, firstNode )
        if ( otherNode == secondNode ):
            return link
    raise Exception( "Internal error." )

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



    
    

