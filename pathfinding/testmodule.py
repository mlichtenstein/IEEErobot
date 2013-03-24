import pygame, sys, math
import nodes as nd
from pygame.locals import *

pygame.init()
screen=pygame.display.set_mode((960,960),0,32)
screen.fill((255,255,255))

radiusCan=33
radiusNode=6
colorCan=(139,137,137) #RGB
colorWood=(160,82,45) #RGB
colorLine=(150,150,100) #RGB
gridColor=(0,105,0) #RGB

blocks = [(273,235,34,34),(960-34,183,34,34),(253,591,34,34),(755,723,34,34)]
circles = [(180,880),(470,590),(480,120)]
lines = ((3,375,273,8),(273,9,373,358),(426,132,656,4),(372,172,706,499),(648,256,446,513),(303,372,300,686),(530,705,5,530))

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
        pygame.display.update()

drawBackground()


number = 0


while 1:
    for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

    if event.type == pygame.MOUSEBUTTONDOWN:
            number += 1
            print number

