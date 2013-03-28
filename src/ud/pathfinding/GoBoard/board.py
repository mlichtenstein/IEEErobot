

import pygame, sys, copy
from pygame.locals import *
pygame.init()

#-------------------------------------------------------------------------------
# Settings
SCALE = 50
SIZE = 19
WIDTH = SIZE*SCALE
HEIGHT = SIZE*SCALE
turn = 'black'
class board:
    list = []
    for i in xrange(SIZE):
        list.append([])
        for j in xrange(SIZE):
             list[i].append(0)

def drawBoard():

    WINDOW = pygame.display.set_mode([WIDTH+SCALE,HEIGHT+SCALE])
    CAPTION = pygame.display.set_caption('Go Board')
    SCREEN = pygame.display.get_surface()
    TRANSPARENT = pygame.Surface([WIDTH,HEIGHT])
    TRANSPARENT.set_alpha(255)
    TRANSPARENT.fill((255,255,255))
    SCREEN.fill((205, 133, 63))

    for i in range(SIZE):
        pygame.draw.line(SCREEN, (0,0,0), (SCALE,i*SCALE+SCALE),(WIDTH,i*SCALE+SCALE),1 )
        pygame.draw.line(SCREEN, (0,0,0), (i*SCALE+SCALE,SCALE),(i*SCALE+SCALE,HEIGHT),1 )
    for i in range(SIZE):
        for j in range(SIZE):
            if board.list[i][j]==1:
                pygame.draw.circle(SCREEN, (255,255,255), (i*SCALE+SCALE,j*SCALE+SCALE), SCALE / 2)
            if board.list[i][j]==-1:
                pygame.draw.circle(SCREEN, (0,0,0), (i*SCALE+SCALE,j*SCALE+SCALE), SCALE / 2)
    pygame.display.flip()


drawBoard()
groupList = []
ignoreList = []
#for each occupied space on the board, not including spaces on the ignoreList:

def checkLibs():
    print '================================='
    del ignoreList[:]
    for i in range(SIZE):
        for j in range(SIZE):

            del groupList[:]
            #print groupList
            if not ( (i,j) in ignoreList or board.list[i][j] == 0 ):
                myColor = board.list[i][j]
                #print myColor
                groupList.append( (i,j) )
                #print "appending"
                #print groupList
                makeGroup( (i,j), myColor )
                #print groupList
            if not groupList == []:
                pass
                #print 'group'
            #check groupList for a liberty that is empty
                liberties = 0
                #print 'the number of items in the group is ' + str(len(groupList))
                for k in range(len(groupList)):
                    ignoreList.append(groupList[k])         #add every element from groupList to ignoreList
                    for (l,m) in [(-1,0),(1,0),(0,-1),(0,1)]:
                            if 0<=groupList[k][0]+l<SIZE and 0<=groupList[k][1]+m<SIZE:
                                if board.list[groupList[k][0]+l][groupList[k][1]+m] == 0:
                                    liberties += 1
                #print 'the number of liberties it has is ' + str(liberties)
                if (liberties == 0): #and not (groupList == latestMove):
                    for groupItem in groupList:
                        board.list[groupItem[0]][groupItem[1]]=0
                        drawBoard()

def makeGroup(point, myColor):
     for (k,l) in [(-1,0), (1,0), (0,-1), (0,1)]:
            #print '1'
            if 0<=point[0]+k<SIZE and 0<=point[1]+l<SIZE:
                    #print '2'
                    if not ( ((point[0]+k),(point[1]+l)) in groupList ):
                        #print '3'
                        if board.list[point[0]+k][point[1]+l] == board.list[point[0]][point[1]]:
                            #print '4'
                            groupList.append( (point[0]+k, point[1]+l) )
                            #print "appending"
                            #print 'the number of items in the group is ' + str(len(groupList))
                            makeGroup( ((point[0]+k),(point[1]+l)), myColor )

     #print groupList







#make a groupList of all the directly edjacent touching stones

#if any stone on this list has an empty neighbor, add all groupList stones to the ignoreList

#if no stone on the groupList has an empty neighbor, set all locations in the groupList to empty

#SecondLastBoardPosition = [123]
#lastBoardPosition = [1235]
#firstTimeFlag=10
#previousBoardPositions = []
flag=0

while True:
    for event in pygame.event.get():
        if event.type==QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            mousex,mousey=event.pos
            distance = SCALE*SIZE
            for i in range(SIZE):
                if abs(i*SCALE+SCALE-mousex)<distance:
                    distance = abs(i*SCALE+SCALE-mousex)
                    xPos=i
            distance = SCALE*SIZE
            for i in range(SIZE):
                if abs(i*SCALE+SCALE-mousey)<distance:
                    distance = abs(i*SCALE+SCALE-mousey)
                    yPos=i
            if board.list[xPos][yPos]==0:

                if turn == 'black':
                    board.list[xPos][yPos]=-1
                    turn = 'white'

                elif turn == 'white':
                    board.list[xPos][yPos]=1
                    turn = 'black'

                drawBoard()
                checkLibs()
