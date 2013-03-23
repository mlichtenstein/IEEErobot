
#   A class for objects useful to making a nice GUI

import pygame
from pygame import *
from robotbasics import *
import math
import easygui as eg

# a class to manage frames:

class Frame:
	def __init__(self, pygame, screen, x_origin, y_origin, width, height):		#the corners on the big canvas
		pygame=pygame
		screen=screen
		self.origin = (x_origin,y_origin)
		self.width = width
		self.height = height
		self.rect = pygame.Rect(x_origin, y_origin, width, height) #the rectangle the frame occupies in the screen
		self.surface = pygame.Surface((width, height))
		self.CC = width/8 #coordconversion switches from feet to pixels
	def update(self):
		self.surface.fill(0x000000)
		self.draw()
		screen.blit(self.surface, self.rect)
	def feelClickDown(self, screen_pos):
		if self.rect.collidepoint(screen_pos):
			pos = (screen_pos[0] - self.origin[0], screen_pos[1] - self.origin[1])
			self.processClickDown(pos)
	def feelClickUp(self, screen_pos):
		if self.rect.collidepoint(screen_pos):
			pos = (screen_pos[0] - self.origin[0], screen_pos[1] - self.origin[1])
			self.processClickUp(pos)	 
	def draw(self):  #this is meant to be overwritten by child classes
		pass
	def processClickDown(self, pos):  #this is meant to be overwritten by child classes
		pass
	def processClickUp(self, pos):  #this is meant to be overwritten by child classes
		pass
	def processMiddleClick(self):
		pass

class Drawable:
	active = True;
	def __init__(self,obj):
		self.obj = obj

class View(Frame): # a frame for representations of physical data (boardView, botView
	state = State()
	selectedHypobot=0
	drawList = list()
	def optionsWindow(self):
		"""dialog = tk.Tk()
		w=tk.label(dialog,text="Select Visibile World Objects:")
		w.pack()
		stop = tk.button(dialog, text ="Done", command = dialog.quit())
		for drawable in drawList:
			
		
		dialog.destroy"""
		pass
	def takeState(self, state):
		self.state = state
	def addObj(self,objList):
		for obj in objList:
			self.drawList.append(Drawable(obj))
	def draw(self):
		for drawable in self.drawList:
			if drawable.active == True:
				drawable.obj.draw(self)

class WorldObj:
	def draw(view):
		pass

class Robot:
	def __init__(self, state, color):
		self.state = state
		self.color = color
	def draw(self, view):
		CC = view.CC
		s = CC*worldConst.robotWidth/2
		xa = s*math.sin(self.state.pose.theta)
		ya = s*math.cos(self.state.pose.theta)
		xb = s*math.cos(self.state.pose.theta)
		yb = s*math.sin(self.state.pose.theta)
		x = self.state.pose.x * CC
		y = self.state.pose.y * CC
		pygame.draw.polygon(view.surface, self.color,
				((x-xa+xb,y+ya+yb),
				(x-xa-xb,y+ya-yb),
				(x+xa-xb,y-ya-yb),
				(x+xa+xb,y-ya+yb)), 1)
				
class Button(Frame): 
	down = False
	downColor = 0x10B62C
	upColor = 0x90EE90
	background = 0x90EE90
	text = "[set text]"
	textColor = (00,00,00,55)
	def __init__(self, pygame, screen, x_origin, y_origin, width, height, text, font, startState):		#the corners on the big canvas
		pygame=pygame
		screen=screen
		self.font=font
		self.origin = (x_origin,y_origin)
		self.width = width
		self.height = height
		self.rect = pygame.Rect(x_origin, y_origin, width, height) #the rectangle the frame occupies in the screen
		self.surface = pygame.Surface((width, height))
		self.text = text
		self.down = startState
	def processClickDown(self, screen_pos):
		self.down = not self.down
	def draw(self):
		if self.down: 
			self.background=self.downColor
		else: 
			self.background=self.upColor
		self.surface.fill(self.background)
		self.drawText()
	def drawText(self):
		tempSurface = self.font.render(self.text, True, self.textColor)
		tempUL = ((self.width-tempSurface.get_width())/2,(self.height-tempSurface.get_height())/2)
		self.surface.blit(tempSurface,tempUL)

class BoardView(View):
	state = State()
	state.pose = Pose(4,4,45)
	robot = Robot(state, (255,255,255))
	drawList = [Drawable(robot)]

class GUI(Frame): 
	pass

if __name__ == "__main__":
	print "Hello World"
	H = 700
	W = 1100
	textHeight = 18

	pygame.init()
	pygame.font.init()
	Font = pygame.font.Font(None, textHeight)
	screen=pygame.display.set_mode((W,H),0,32)
	screen.fill((127,127,127))
	#set up frames:
	#BoardView = boardView(pygame, screen, 5, 30, 540, 540, LandmarkList, LogList, EyeList)
	#BoardView.takeBestGuessBot(BestGuessBot)
	#buttons for BoardView:

	boardView=BoardView(pygame, screen, 10, 10, 540, 540)
	runNum = 0

	frameList = []
	frameList.append(boardView)

	"""----------------MAIN LOOP -------------------"""
	while runNum >= 0:
		for event in pygame.event.get():
			if event.type==QUIT:
				pygame.quit()
				sys.exit()		
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					for frame in frameList:
						frame.feelClickDown(pygame.mouse.get_pos())
			if event.type == MOUSEBUTTONUP:
				if event.button == 1:
					for frame in frameList:
						frame.feelClickUp(pygame.mouse.get_pos())
				if event.button == 2:
					for frame in frameList:
						frame.feelMiddleClick()

		boardView.takeState()				
		boardView.update()
		pygame.display.update()
		#runNum -= 1
