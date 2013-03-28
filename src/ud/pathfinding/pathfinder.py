import pygame, sys, math, io, random
from pygame.locals import *

pygame.init()
screen=pygame.display.set_mode((960,960),0,32)
colorCan=(139,137,137) #RGB
colorWood=(160,82,45) #RGB
colorLine=(150,150,100) #RGB
gridColor=(0,105,0) #RGB
radius=33
x1,y1,x2,y2 = 0,0,0,0
blocks = [(273,235,34,34),(960-34,183,34,34),(253,591,34,34),(755,723,34,34)]
circles = [(180,880),(470,590),(480,120)]
lines = ((3,375,273,8),(273,9,373,358),(426,132,656,4),(372,172,706,499),(648,256,446,513),(303,372,300,686),(530,705,5,530))
walls = (0,0,960,960)

def drawBackground():
        screen=pygame.display.set_mode((960,960),0,32)
        drawObjects()

def drawBot(x,y,theta):
        theta = theta * math.pi/180
        pygame.draw.polygon(screen, (205,205,205), ((x+60*math.cos(theta)-60*math.sin(theta),y-60*math.sin(theta)-60*math.cos(theta)),(x-60*math.cos(theta)-60*math.sin(theta),y+60*math.sin(theta)-60*math.cos(theta)),(x-60*math.cos(theta)+60*math.sin(theta),y+60*math.sin(theta)+60*math.cos(theta)),(x+60*math.cos(theta)+60*math.sin(theta),y-60*math.sin(theta)+60*math.cos(theta))), 1)
        #pygame.draw.rect(screen, (255,255,255), (x+60,y+60,120,120))
        pygame.display.update()

def drawObjects():
        screen.lock()
        #for i in range(1,4):
        #    pygame.draw.line(screen,gridColor,(0,i*240),(960,i*240),1)
        #    pygame.draw.line(screen,gridColor,(i*240,0),(i*240,960),1)
        for block in blocks:
            pygame.draw.rect(screen, colorWood, block)
        for circle in circles:
            pygame.draw.circle(screen, colorCan, circle, radius)
        for line in lines:
            pygame.draw.line(screen,colorLine, (1.357*line[0],1.357*line[1]),(1.357*line[2],1.357*line[3]), 20)
        screen.unlock()
        pygame.display.update()

def generateRandomNode():
    x = random.randint(0,960) # 10*96 inches or 8 feet
    y = random.randint(0,960) # 10*96 inches or 8 feet
    theta = random.randint(0,259)
    return ([x,y,0,0])

def generateNode(node):
    distanceShortest = 10**11
    for i in range(100):
        x,y = node[0],node[1] #starting point
        oldDistance = math.hypot(x-end[0],y-end[1])
        r=random.gauss(60,5) # add 1 foot
        if oldDistance<120:
            r=oldDistance
        #rBest=r
        theta = random.randint(0,360)
        #thetaBest=theta
        newX=x+r*math.cos(math.pi/180*theta)
        newY=y+r*math.sin(math.pi/180*theta)
        distance=math.hypot(newX-end[0],newY-end[1]) #distance to end

        #for line in lines:
        #    if math.hypot(x+r*math.cos(math.pi/180*theta)-line[0],y+r*math.sin(math.pi/180*theta)-line[1])<=105:
        #        distance+=10**10
        for circle in circles:
            if math.hypot(x+r*math.cos(math.pi/180*theta)-circle[0],y+r*math.sin(math.pi/180*theta)-circle[1])<=105:
                distance+=10**10
            distance += 10**2/math.hypot(x+r*math.cos(math.pi/180*theta)-circle[0],y+r*math.sin(math.pi/180*theta)-circle[1])**2
        for block in blocks:
            if math.hypot(x+r*math.cos(math.pi/180*theta)-block[0],y+r*math.sin(math.pi/180*theta)-block[1])<=105:
                distance+=10**10
            distance += 10**2/math.hypot(x+r*math.cos(math.pi/180*theta)-block[0]+17,y+r*math.sin(math.pi/180*theta)-block[1]+17)**2
       # distance += 100/abs(newX-960)**2 + 100/abs(newX-0)**2 + 100/abs(newY-0)**2 + 100/abs(newY-960)**2
        if abs(newX-960)<80 or abs(newX-0)<80:
            distance+=10**10
        if abs(newY-960)<80 or abs(newY-0)<80:
            distance+=10**10

        if distance<distanceShortest:
            rBest=r
            thetaBest=theta
            distanceShortest=distance
    return([x+rBest*math.cos(math.pi/180*thetaBest),y+rBest*math.sin(math.pi/180*thetaBest),0,parent])

def drawLines(x1,y1,x2,y2):
    screen.lock()
    pygame.draw.line(screen, (255,255,255), (x1,y1), (x2,y2), 3)
    screen.unlock()
    pygame.display.update()

def penalizeBranch(index,penalty):
    nodes[index][2]+=penalty #penalty
    for i in range(1,len(nodes)):
        nodes[index][2]+=penalty #penalty
        if nodes[i][3]==index:
            penalizeBranch(i, penalty)

penalty=0
flag=0

drawBackground()
#pygame.draw.line(screen, (255,255,255), (480,480), (480+300*math.cos(math.pi*45/180),480+300*math.sin(math.pi*45/180)), 9)
drawBot(100,100,0)

nodes = [] #nodes[index][x, y, penalty, parent]
start = [random.randint(0,960),random.randint(0,960),0,0]
pygame.draw.circle(screen, (0,255,0), (start[0],start[1]), 10)
end   = [random.randint(120,840),random.randint(120,840),0,0]
pygame.draw.circle(screen, (255,0,0), (end[0],end[1]), 10)
nodes.append(start)
bestNode=0


while math.hypot(nodes[-1][0]-end[0],nodes[-1][1]-end[1])>10:
    leastPenalty=nodes[0][2]
    #find least penalized node from nodes
    for i in range(len(nodes)):
        if nodes[i][2]<=leastPenalty:
            leastPenalty=nodes[i][2]
            parent=i

    #generate child node from parent node (and penalize it for its own problems)
    child=generateNode(nodes[parent])
    nodes.append(child)

    screen.lock()
    pygame.draw.line(screen, (0,random.randint(1,255),random.randint(1,255)), (nodes[-1][0],nodes[-1][1]), (nodes[parent][0],nodes[parent][1]), 1)
    screen.unlock()
    pygame.display.update()
    penalizeBranch(parent,child[2])
    #penalty+=1
    for event in pygame.event.get():
        if event.type==QUIT:
            pygame.quit()
            sys.exit()
while 1:
    if flag==0:
        if not nodes[child[3]][3]==-1:
            screen.lock()
            pygame.draw.line(screen, (255,0,0), (child[0],child[1]), (nodes[child[3]][0],nodes[child[3]][1]), 2)
            child=nodes[child[3]]
            screen.unlock()
            pygame.display.update()
        else:
            screen.lock()
            pygame.draw.line(screen, (255,0,0), (child[0],child[1]), (nodes[child[3]][0],nodes[child[3]][1]), 2)
            child=nodes[child[3]]
            screen.unlock()
            pygame.display.update()
            flag=1

    for event in pygame.event.get():
        if event.type==QUIT:
            pygame.quit()
            sys.exit()
