import math

class Graph:
    def __init__( self ):
        self.nodes = list()
        self.links = list()
        
    def addNode( self, x, y):
        self.nodes.append(Node(x,y))

    def addLink( self, node1, node2, (r,g,b) ):
        self.links.append( Link (node1,node2,(r,g,b)) )

    def removeNode( self, node):
        linksRemoved=0
        for link in self.links:
            if link.node1 == node or link.node2 == node:
                self.links.remove(link)
                self.removeNode(node)
                linksRemoved+=1
                break
        if linksRemoved==0:
            self.nodes.remove(node)


#===================================NODE===================================#
# XPos                -----      X position of the node
# Ypos                -----      Y position of the node
# theta(optional)     -----      angle to grab puck(optional)
# puck(optional)      -----      1-16 representing which puck it can reach (optional)
#===================================NODE===================================#
class Node:
    def __init__(self, XPos, YPos):
        self.X = XPos
        self.Y = YPos
        self.theta = 361
        self.puck = -1
        self.radius = 10
        self.localize = 0
#===================================LINK===================================#
# node1               -----      node from
# node2               -----      node to
# log (optional)      -----      binary 1/0 if there is/is not a log (optional)
# theta (optional)    -----      the direction a bot must face while moving (optional)
# length              -----      length of the link is set automatically
#===================================LINK===================================#
class Link:
    def __init__( self, node1, node2, (r,g,b) ):
        self.red = r
        self.green = g
        self.blue = b
        self.logOffset = 0 # edit this to change percieved length of link due to a log
        self.node1 = node1
        self.node2 = node2
        self.node1direction = -180/math.pi*math.atan2(self.node2.Y-self.node1.Y,self.node2.X-self.node1.X)
        self.node2direction = -180/math.pi*math.atan2(self.node1.Y-self.node2.Y,self.node1.X-self.node2.X)
        self.log = 0
        self.update()
    def update( self ):
        print "called update"
        self.length = math.hypot(self.node1.X-self.node2.X,self.node1.Y-self.node2.Y)+self.log*self.logOffset
        if self.node1.X > self.node2.X:
            #h is for horizontal
            #v is for verticality
            self.node1h="right"
            self.node2h="left"
        else:
            self.node1h="left"
            self.node2h="right"
            
        if self.node1.Y < self.node2.Y:
            self.node1v="top"
            self.node2v="bottom"
            
        else:
            self.node1v="bottom"
            self.node2v="top"

#===================================bot====================================#
#                 contains pose data (x, y, theta)
#===================================LINK===================================#     
class Pose:
    def __init__( self ):
        self.X = 0
        self.Y = 0
        self.theta = 0
        

