import pygame, sys, math, graph
from pygame.locals import *

pygame.init()
screen=pygame.display.set_mode((960,960),0,32)
screen.fill((255,255,255))
radius=10
nodes = []
links = []
drawFlag = 1
colorCan=(139,137,137) #RGB
colorWood=(160,82,45) #RGB
colorLine=(150,150,100) #RGB
gridColor=(0,105,0) #RGB
radiusCan=33
x1,y1,x2,y2 = 0,0,0,0
blocks = [(273,235,34,34),(960-34,183,34,34),(253,591,34,34),(755,723,34,34)]
circles = [(180,880),(470,590),(480,120)]
lines = ((3,375,273,8),(273,9,373,358),(426,132,656,4),(372,172,706,499),(648,256,446,513),(303,372,300,686),(530,705,5,530))

def drawObjects():
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
        pygame.display.update()

def drawBot(x,y,theta):
        theta = theta * math.pi/180
        pygame.draw.polygon(screen, (205,205,205), ((x+60*math.cos(theta)-60*math.sin(theta),y-60*math.sin(theta)-60*math.cos(theta)),(x-60*math.cos(theta)-60*math.sin(theta),y+60*math.sin(theta)-60*math.cos(theta)),(x-60*math.cos(theta)+60*math.sin(theta),y+60*math.sin(theta)+60*math.cos(theta)),(x+60*math.cos(theta)+60*math.sin(theta),y-60*math.sin(theta)+60*math.cos(theta))), 1)
        #pygame.draw.rect(screen, (255,255,255), (x+60,y+60,120,120))
        pygame.display.update()

def whatNode((x,y)):
    nearestNode=0
    distance=960**2
    distanceLowest = 960**2
    for i in range(len(nodes)):
        distance = math.hypot(x-nodes[i][0],y-nodes[i][1])
        if distance<distanceLowest:
            nearestNode=i
            distanceLowest=distance
    return (nearestNode, distanceLowest)


while 1:

    #bot movement
        #for bot to travel from (x1,y1) to (x2,y2)
            #bot should already be at (x1,y1) with some theta
            #rotate to face x2,y2
            #step in the direction
            #stop on arrival


    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            posDown=pygame.mouse.get_pos()
            downNode=whatNode(posDown)[0]
            #note which node it is in
            drawFlag = 1


        elif event.type == pygame.MOUSEBUTTONUP:
            screen.fill((255,255,255))
            posUp = pygame.mouse.get_pos()
            upNode = whatNode(posDown)[0]
            #if in the same node, then:
            drawFlag = 1

            clickTravel = math.hypot(posDown[0]-posUp[0],posDown[1]-posUp[1])

            if whatNode(posDown)[1] <= radius:   #if click was inside a node
                if whatNode(posUp)[1] <= radius:  #and  unclick was inside a node
                    if whatNode(posDown)[0]==whatNode(posUp)[0]:  #and those were the same nodes
                        minusi = 0
                        for i in range(len(links)):#remove all links to the node and then
                                i-=minusi
                                if links[i][0]==nodes[whatNode(posDown)[0]][0] and links[i][1]==nodes[whatNode(posDown)[0]][1]:
                                    links.pop(i)
                                    minusi+=1
                                elif links[i][1]==nodes[whatNode(posDown)[0]][0] and links[i][0]==nodes[whatNode(posDown)[0]][1]:
                                    links.pop(i)
                                    minusi+=1
                                elif links[i][2]==nodes[whatNode(posDown)[0]][0] and links[i][3]==nodes[whatNode(posDown)[0]][1]:
                                    links.pop(i)
                                    minusi+=1
                                elif links[i][3]==nodes[whatNode(posDown)[0]][0] and links[i][2]==nodes[whatNode(posDown)[0]][1]:
                                    links.pop(i)
                                    minusi+=1
                        nodes.remove(nodes[whatNode(posDown)[0]])  #remove that node
                    else: # but if they were two different nodes
                        links.append((nodes[whatNode(posDown)[0]][0],nodes[whatNode(posDown)[0]][1],nodes[whatNode(posUp)[0]][0],nodes[whatNode(posUp)[0]][1]))#then make a link between

            else: # clicked not on a node
                if clickTravel <= radius: #clicked and didnt drag
                    nodes.append((posDown[0],posDown[1],-1))
                elif clickTravel > radius: #clicked and dragged
                    nodes.append((posDown[0],posDown[1],math.atan2(posUp[0]-posDown[0],posUp[1]-posDown[1])))

    if drawFlag ==1:
        drawObjects()
        for i in range(len(nodes)):#print nodes
            pygame.draw.circle(screen,(0,0,0),(nodes[i][0],nodes[i][1]), radius)
            if not (nodes[i][2] == -1):
                pygame.draw.line(screen,(255,100,50),(nodes[i][0],nodes[i][1]),(nodes[i][0]+radius*2*math.sin(nodes[i][2]),nodes[i][1]+radius*2*math.cos(nodes[i][2])),1)

        for l in range(len(links)):#print links
            pygame.draw.line(screen, (0,200,255), (links[l][0],links[l][1]),(links[l][2],links[l][3]),2)

        drawBot(120,120,10)
        pygame.display.update()
        drawFlag=0

