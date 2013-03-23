import pygame, sys, math
import nodesnew as nd
from pygame.locals import *

pygame.init()
screen=pygame.display.set_mode((960,960),0,32)
screen.fill((255,255,255))

radiusCan=33
radiusNode=10
colorCan=(139,137,137) #RGB
colorWood=(160,82,45) #RGB
colorLine=(150,150,100) #RGB
gridColor=(0,105,0) #RGB

blocks = [(273,235,34,34),(960-34,183,34,34),(253,591,34,34),(755,723,34,34)]
circles = [(180,880),(470,590),(480,120)]
lines = ((3,375,273,8),(273,9,373,358),(426,132,656,4),(372,172,706,499),(648,256,446,513),(303,372,300,686),(530,705,5,530))

def drawBot(x,y,theta):
        theta = theta * math.pi/180
        pygame.draw.polygon(screen, (0,0,0), ((x+60*math.cos(theta)-60*math.sin(theta),y-60*math.sin(theta)-60*math.cos(theta)),(x-60*math.cos(theta)-60*math.sin(theta),y+60*math.sin(theta)-60*math.cos(theta)),(x-60*math.cos(theta)+60*math.sin(theta),y+60*math.sin(theta)+60*math.cos(theta)),(x+60*math.cos(theta)+60*math.sin(theta),y-60*math.sin(theta)+60*math.cos(theta))), 1)
        #pygame.draw.rect(screen, (255,255,255), (x+60,y+60,120,120))
        pygame.display.update()

def drawBackground():
        screen.fill((255,255,255))
        screen.lock()
        for i in range(1,4):
            pygame.draw.line(screen,gridColor,(0,i*240),(960,i*240),1)
            pygame.draw.line(screen,gridColor,(i*240,0),(i*240,960),1)
        for block in blocks:
            pygame.draw.rect(screen, colorWood, block)
        for circle in circles:
            pygame.draw.circle(screen, colorCan, circle, radiusCan)
        for line in lines:
            pygame.draw.line(screen,colorLine, (1.357*line[0],1.357*line[1]),(1.357*line[2],1.357*line[3]), 20)
        screen.unlock()

def closestNodeToNode(currentNode):
        minDistance=10**10
        nearestNode = 0
        for i in nd.nodes:
            distance = math.hypot((i.pos.X-currentNode.pos.X),(i.pos.Y-currentNode.pos.Y))
            if distance <= minDistance:
                minDistance = min(minDistance, distance)
                nearestNode = i
        return (nearestNode)

def closestNodeToPoint( X,Y ):
        minDistance=10**10
        nearestNode = 0
        for i in nd.nodes:
            distance = math.hypot((i.pos.X-X),(i.pos.Y-Y))
            if distance <= minDistance:
                minDistance = min(minDistance, distance)
                nearestNode = i
        return (nearestNode, minDistance)


def nodeOrNot( X, Y ):
        minDistance=radiusNode+1
        for i in nd.nodes:
            distance = math.sqrt((i.pos.X-X)**2+(i.pos.Y-Y)**2)
            if (distance <= minDistance):
                if not distance==0:
                    minDistance = distance
        if minDistance<=radiusNode:
            return 1
        else:
            return 0

    #return boolean true=1 if it is a node, false=0 if it is not a node

def drawLinks():
    for node in nd.nodes:
        for link in node.links:
            print link.pos.X
            pygame.draw.line(screen,(10,98,154), (link.pos.X,link.pos.Y),(node.pos.X,node.pos.Y), 3)

def drawNodes():

        for i in nd.nodes:
            pygame.draw.circle(screen,(215,235,255), (i.pos.X, i.pos.Y) , radiusNode)
            pygame.draw.circle(screen,(0,10,20), (i.pos.X, i.pos.Y) , radiusNode, 1)

drawFlag = 1
mouseFlag =0
upFlag=1
downFlag=0

while 1:
    if drawFlag == 1:
        drawBackground()
        drawLinks()
        drawNodes()
        pygame.display.update()
        drawFlag = 0

    for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

    if event.type == pygame.MOUSEBUTTONDOWN:
            posDown=pygame.mouse.get_pos() #record xy position as tuple

            downFlag=1
            if upFlag == 1:
                    upFlag=0
                    drawFlag = 1
                    if not nd.nodes == []:
                            if nodeOrNot(posDown[0],posDown[1]) == 1:
                                clickedNode = closestNodeToPoint(posDown[0],posDown[1])[0]
                                appendedFlag = 0
                            else:
                                nd.nodes.append(nd.Node( posDown[0], posDown[1]) )
                                appendedFlag = 1
                    elif nd.nodes == []:
                          nd.nodes.append(nd.Node( posDown[0], posDown[1]) )
                          appendedFlag = 1

               #if so, we know what node you clicked on
               #store this as the clickedNode

    if event.type == pygame.MOUSEBUTTONUP:
            upFlag=1
            posUp=pygame.mouse.get_pos()
            if downFlag == 1:
                drawFlag=1
                downFlag=0
                unclickedNode = closestNodeToPoint(posUp[0],posUp[1])[0]
                if appendedFlag == 0:
                    if clickedNode == unclickedNode and closestNodeToPoint(posUp[0],posUp[1])[1]<radiusNode:
                        print "same node"
                        nd.nodes.remove(clickedNode)
                    elif nodeOrNot(posUp[0],posUp[1]) == 1:
                        clickedNode.links.append(unclickedNode)
                        unclickedNode.links.append(clickedNode)
                        print "dragged from a node to a node"

                    elif nodeOrNot(posUp[0],posUp[1]) == 0:
                        print "dragged from a node into space"
                        nd.nodes.append(nd.Node( posUp[0], posUp[1]))
                        unclickedNode = closestNodeToPoint(posUp[0],posUp[1])[0]
                        clickedNode.links.append(unclickedNode)
                        unclickedNode.links.append(clickedNode)


