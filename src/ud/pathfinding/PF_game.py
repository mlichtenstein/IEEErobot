from time import *
import serial
import math
import numpy
import pygame, sys, math, io
from pygame.locals import *
from pygame import *
from decimal import Decimal
import copy
import time

print(time)

#settings:
eyeNum = 2

"""----------------Matt Bird's code HERE --------------------------------"""
def patchArray(localArray):
	
    #fix edge behavior
    if localArray[0]>1.3*localArray[1]:
        localArray[0]=localArray[1]
    if localArray[180]>1.3*localArray[179]:
        localArray[180]=localArray[179]
    #fix lines that run through objects
    for i in range(2,178):
        if localArray[i-1]>1.5*localArray[i] and localArray[i+1]>1.5*localArray[i]:
            localArray[i] = (localArray[i-1]+localArray[i+1])/2
    return localArray

def circleDetection(x1, y1, heading, landmarkList):
	#START a little wrapper, gets copied below
	circles = list()
	squares = list()
	radius=0
	for landmark in landmarkList:
		if landmark.landmarkType=="ROCK":
			circles.append((landmark.x, landmark.y))
			radius=landmark.rockRadius
	#END of wrapper
	array=[0.0]*181
	print(x1,y1, radius, heading)
    #phi is the sensor angle relative to the bot
	for phi in range(181):
		angle = 90.0+heading-phi
		h = math.tan(math.pi / 180 * (angle+90))
		h = math.tan(math.pi / 180 * (angle+90))
		if (not h==0) and (not h**2+1==0):
			r = 222.0
			for circle in circles:
				a = circle[0]
				b = circle[1]
				k = y1+x1/h-b
				try:
					#Generate collisions IR sensor should expect to see. One positive and one negative for both sides of the circle.
					x_intercept1 = ((-math.sqrt(-(a**2)*(h**2)+2*a*(h**3)*k+(h**4)*-(k**2)+(h**4)*(radius**2)+(h**2)*(radius**2)))+a*(h**2)+h*k)/(h**2+1)
					x_intercept2 = (( math.sqrt(-(a**2)*(h**2)+2*a*(h**3)*k+(h**4)*-(k**2)+(h**4)*(radius**2)+(h**2)*(radius**2)))+a*(h**2)+h*k)/(h**2+1)
					y_intercept1 =(-x_intercept1/h+y1+x1/h)
					y_intercept2 =(-x_intercept2/h+y1+x1/h)
					#print(x_intercept1,x_intercept2,y_intercept1,y_intercept2)
					#Use only the shortest distance.
					if math.hypot(x1-x_intercept1,y1-y_intercept1)<math.hypot(x1-x_intercept2,y1-y_intercept2):
						x_intercept = x_intercept1
						y_intercept = y_intercept1
					elif math.hypot(x1-x_intercept1,y1-y_intercept1)>math.hypot(x1-x_intercept2,y1-y_intercept2):
						x_intercept = x_intercept2
						y_intercept = y_intercept2
                    #Remove the back side of the rays (the part behind the sensor)
					if (heading+90 > 180/math.pi*math.atan2(y_intercept-y1, x_intercept-x1) > heading-90):
						r=min(math.hypot(x1-x_intercept,y1-y_intercept),r)
					elif (heading+90+360 > 180/math.pi*math.atan2(y_intercept-y1, x_intercept-x1) > heading-90+360):
						r=min(math.hypot(x1-x_intercept,y1-y_intercept),r)
					elif (heading+90-360 > 180/math.pi*math.atan2(y_intercept-y1, x_intercept-x1) > heading-90-360):
						r=min(math.hypot(x1-x_intercept,y1-y_intercept),r)
					print(r)
                #exception executes when there are no collisions
				except:
					pass
			#store radius into array
			array[phi]=r
	#patch up array
	print(array)
	array = patchArray(array)
	return array

def squareDetection(array, x1, y1, heading, landmarkList):
	#START a little wrapper
	blocks = list()
	for landmark in landmarkList:
		if landmark.landmarkType=="TREE":
			s = landmark.treeSide
			blocks.append((landmark.x - s/2, landmark.y - s/2, s, s))
	#END of wrapper
	for phi in range(181):
		slope = math.tan(math.pi / 180 * (heading+90-phi))
		#y1=slope*x1+b1, so b1=y1-slope*x1
		b1 = y1-slope*x1
		#blocks = [(920,210,40,40),(272,272,40,40),(239,602,40,40),(747,747,40,40)]
		for square in blocks:
			#xl means x of the blocks left side (t is top, r is right, b is bottom)
			xr = square[0]
			yt = square[1]
			xl = square[0]+square[2]
			yb = square[1]+square[3]
			#yline means y of the line, xl is x is the line

			yline=slope*xl+b1
			if yb>yline>yt:
				#collision at xb,yline
				if (heading+90 > 180/math.pi*math.atan2(yline-y1, xl-x1) > heading-90):
					array[phi]= min(array[phi],math.hypot(x1-xl,y1-yline))
				elif (heading+90+360 > 180/math.pi*math.atan2(yline-y1, xl-x1) > heading-90+360):
					array[phi]= min(array[phi],math.hypot(x1-xl,y1-yline))
				elif (heading+90-360 > 180/math.pi*math.atan2(yline-y1, xl-x1) > heading-90-360):
					array[phi]= min(array[phi],math.hypot(x1-xl,y1-yline))
			yline=slope*xr+b1
			if yb>yline>yt:
				#collision at xb,yline
				if (heading+90 > 180/math.pi*math.atan2(yline-y1, xr-x1) > heading-90):
					array[phi]= min(array[phi],math.hypot(x1-xr,y1-yline))
				elif (heading+90+360 > 180/math.pi*math.atan2(yline-y1, xr-x1) > heading-90+360):
					array[phi]= min(array[phi],math.hypot(x1-xr,y1-yline))
				elif (heading+90-360 > 180/math.pi*math.atan2(yline-y1, xr-x1) > heading-90-360):
					array[phi]= min(array[phi],math.hypot(x1-xr,y1-yline))

			if slope==0:
				slope=.01

			xline = (yb-b1)/slope
			if xl>xline>xr:
				if (heading+90 > 180/math.pi*math.atan2(yb-y1, xline-x1) > heading-90):
					array[phi]= min(array[phi],math.hypot(x1-xline,y1-yb))
				if (heading+90+360 > 180/math.pi*math.atan2(yb-y1, xline-x1) > heading-90+360):
					array[phi]= min(array[phi],math.hypot(x1-xline,y1-yb))
				if (heading+90-360 > 180/math.pi*math.atan2(yb-y1, xline-x1) > heading-90-360):
					array[phi]= min(array[phi],math.hypot(x1-xline,y1-yb))

			xline = (yt-b1)/slope
			if xl>xline>xr:
				if (heading+90 > 180/math.pi*math.atan2(yt-y1, xline-x1) > heading-90):
					array[phi]= min(array[phi],math.hypot(x1-xline,y1-yt))
				if (heading+90+360 > 180/math.pi*math.atan2(yt-y1, xline-x1) > heading-90+360):
					array[phi]= min(array[phi],math.hypot(x1-xline,y1-yt))
				if (heading+90-360 > 180/math.pi*math.atan2(yt-y1, xline-x1) > heading-90-360):
					array[phi]= min(array[phi],math.hypot(x1-xline,y1-yt))
	array = patchArray(array)
	return array

"""----------------Max's Sim code-------------------------"""

def calcIdealRange(x_eye, y_eye, theta_board, landmarkList): #theta_board is WRT board
	r = 5.0
	theta_board = theta_board * math.pi/180  #math like this prefers to be done in radians
	circles = list()
	squares = list()
	radius=0
	side = 0
	for landmark in landmarkList:
		if landmark.landmarkType=="ROCK":
			circles.append((landmark.x, landmark.y, landmark.rockRadius))
		else:
			#change to squares.append if you implement special handling for squares
			circles.append((landmark.x, landmark.y, landmark.treeSide * math.sqrt(2)/2))
			side = landmark.treeSide
	"""
	for square in squares:
		delta_x = square[0] - x_eye
		delta_y = - (square[1] - y_eye) # leading minus cuz y is down-positive	
		corners = []
		corners.append((landmark.x + side/2,landmark.y - side/2))
		corners.append((landmark.x - side/2,landmark.y - side/2))
		corners.append((landmark.x - side/2,landmark.y + side/2))
		corners.append((landmark.x + side/2,landmark.y + side/2))
		corners.append(corners[0])
		for i in range(4):
			thetas = []
			thetas.append(math.atan2(corners[i][0],corners[i][1]))
			thetas.append(math.atan2(corners[i+1][0],corners[i+1][1]))
			for theta in thetas:
				if theta < 0:
					theta += 2* math.pi
			#print(thetas)
			thetas.sort()
			if thetas[0]<= theta_board and theta_board <= thetas[1]:
				if corners[i][0] != corners[i+1][0]: # means x values are equal => vertical line
					r = abs(delta_x/math.cos(theta_board))
				else: #horiz line:
					r = abs(delta_y/math.cos(theta_board-90))
					"""
	for circle in circles:
		delta_x = circle[0] - x_eye
		delta_y = - (circle[1] - y_eye) # leading minus cuz y is down-positive
		radius = circle[2]
		theta_BL = math.atan2(delta_y, delta_x)
		while theta_board > math.pi:
			theta_board -= 2* math.pi
		theta = theta_board - theta_BL

		#print("x:",circle.x, x_eye, delta_x)
		#print("y:",circle.y, y_eye, delta_y)
		#print("theta:", theta_BL*180/math.pi, theta_eye*180/math.pi, theta*180/math.pi)
		
		d = math.sqrt(delta_x**2 + delta_y**2)
		if d < radius:
			return 0
		lim = math.asin(radius/d)
		#print("Lim:", lim*180/math.pi)
		if abs(theta) < lim :
			try:
				r = min(r,d*(math.cos(theta) - math.sqrt((radius/d)**2 - math.sin(theta)**2)))
			except:
				print("GAAAH!",x_eye, y_eye, theta, d)
	return r
"""----------------GENERAL (template) CLASSES----------------------------"""

# a class to manage frames:
class frame:
	def __init__(self, pygame, screen, x_origin, y_origin, width, height):		#the corners on the big canvas
		pygame=pygame
		screen=screen
		self.origin = (x_origin,y_origin)
		self.width = width
		self.height = height
		self.rect = pygame.Rect(x_origin, y_origin, width, height) #the rectangle the frame occupies in the screen
		self.surface = pygame.Surface((width, height))
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

class view(frame): # a frame for representations of physical data (boardView, botView
	hypobotList = list()
	selectedHypobot = 0
	def takeHypobotList(self, hypobotList, selectedHypobot):
		self.hypobotList = hypobotList
		self.selectedHypobot = selectedHypobot	
	def takeEyeList(self, eyeList):
		self.localEyeList = eyeList
	def takeLandmarkList(self, landmarkList):
		self.localLandmarkList = landmarkList
	
class button(frame): 
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


class landmark:
	x,y = 0,0 #in feet, of course
	landmarkType = None
	rockRadius = 6.7/12/2
	treeSide = 3.5/12
	rockColor = 0xADADAD
	treeColor = 0x8B6914
	def __init__(self, x, y, landmarkType):
		self.x,self.y,self.landmarkType= (x,y,landmarkType)
	def draw(self, coordConversion, surface):
		pos = (int(self.x/coordConversion), int(self.y/coordConversion))
		radius = int(self.rockRadius/coordConversion)
		side = int(self.treeSide/coordConversion)
		if self.landmarkType == "ROCK":
			pygame.draw.circle(surface, self.rockColor, pos, radius)
		if self.landmarkType == "TREE":
			rect = (pos[0] - side/2, pos[1]-side/2, side, side)
			pygame.draw.rect(surface, self.treeColor, rect)
"""-----------------SPECIFIC CLASSES-----------------"""

def drawRange(surface, color, origin_x, origin_y, theta, pos, distance):
	start_x = origin_x + 10*math.cos((theta + pos)*math.pi/180)
	start_y = origin_y - 10*math.sin((theta + pos)*math.pi/180)
	end_x = origin_x + distance*math.cos((theta + pos)*math.pi/180)
	end_y = origin_y - distance*math.sin((theta + pos)*math.pi/180)
	pygame.draw.line(surface, color, (start_x,start_y), (end_x, end_y))

def drawRangeArray(surface, color, x, y, theta, array):
	for i in range(len(array)):
		drawRange(surface, color, x, y, theta, i, array[i])

class botView(view):
	coordConversion =8.0 / 540 #feet/pixels
	realEyeVisible = [True]*4
	idealEyeVisible = [True]*4
	def draw(self):
		print(self.realEyeVisible,self.idealEyeVisible)
		for eye in self.localEyeList:
			x_origin = int(self.width/2 + (eye.x_offset)/self.coordConversion)
			y_origin = int(self.height/2 + (eye.y_offset)/self.coordConversion)
			if self.idealEyeVisible[eye.eyeNum]:
				hypobot = self.hypobotList[self.selectedHypobot]
				color = 0x0000FF
				for i in range (181):
					drawRange(self.surface,color, x_origin, y_origin, eye.theta_offset, i, hypobot.localEyeList[eye.eyeNum].IR[i]/self.coordConversion) 
			if self.realEyeVisible[eye.eyeNum]:
				for i in range(181):
					dist=eye.IR[i]/self.coordConversion
					if eye.eyeNum == 0:
						color = (0xFF, 0, 0, 0x22)
					else: color = (0x88, 0x88, 0, 0x22)
					drawRange(self.surface, color, x_origin, y_origin, eye.theta_offset,i, dist)
			
class boardView(view): #boardFrame inheirits frame
	coordConversion =8.0 / 540 #feet/pixels
	def __init__(self, pygame, screen, x_origin, y_origin, width, height,LandmarkList, EyeList):		#the corners on the big canvas
		pygame=pygame
		screen=screen
		self.origin = (x_origin,y_origin)
		self.width = width
		self.height = height
		self.rect = pygame.Rect(x_origin, y_origin, width, height) #the rectangle the frame occupies in the screen
		self.surface = pygame.Surface((width, height))
		self.landmarkList = LandmarkList
		self.EyeList = EyeList
	def processClick(self, screen_pos):
		coordConversion = 8.0 / self.width #convert to feet
		#print(screen_pos)
		board_pos = (coordConversion * screen_pos[0], coordConversion * screen_pos[1])
		#print("You clicked at "+str(board_pos[0])+","+str(board_pos[1])+" ft")
	def draw(self):
		coordConversion = 8.0 / self.width #convert to feet
		if LandmarkToggleButton.down:
			for landmark in self.landmarkList:
				landmark.draw(self.coordConversion, self.surface)
		for i in range(len(self.hypobotList)):
			hypobot = self.hypobotList[i]
			alpha = 255-int(hypobot.weight*255)
			color = (0xFF,00,00,alpha)
			pos = (int(hypobot.x/self.coordConversion), int(hypobot.y/self.coordConversion))
			pygame.draw.circle(self.surface, color, pos, 5,1)
			drawRange(self.surface, color, pos[0], pos[1], hypobot.theta, 0, 0)
			#draw SelectedHypobot:
			"""
			print("1",id(hypobot))
			print("2",id(HypobotList[SelectedHypobot]))
			print("3",id(self.hypobotList[self.selectedHypobot]))
			"""
			#sys.exit()
			if i == SelectedHypobot:
				pygame.draw.circle(self.surface, 0xFFFFFF, pos, 6, 1)
				#hypobot.generateEyeData(self.localEyeList, self.localLandmarkList)
				drawRange(self.surface, 0xFFFFFF, hypobot.x/self.coordConversion, hypobot.y / self.coordConversion, hypobot.theta, 0, 5)
				for eye in hypobot.localEyeList:
					for i in range(len(eye.IR)):
						theta = hypobot.theta
						color =  0x0000FF
						#print (eye.eyeNum,theta + eye.theta_offset)
						x = int((hypobot.x + eye.x_offset*math.cos(theta) + eye.y_offset*math.sin(theta))/self.coordConversion)
						y = int((hypobot.y - eye.x_offset*math.sin(theta) + eye.y_offset*math.cos(theta))/self.coordConversion)
						drawRange(self.surface,color, x, y, theta + eye.theta_offset, i, self.localEyeList[eye.eyeNum].IR[i]/self.coordConversion) 
						pygame.display.update()
						
						
class bot:
	def __init__(self, x, y, theta):
		self.y = y
		self.x = x
		self.theta = theta

class hypobot(bot): #hypobot inheirits bot:
	weight = 1
	localEyeList = list()
	def changeWeight(self, real_eyeList, landmarkList):
		if len(real_eyeList)!= len(self.eyeList):
			print("eyeList mismatch!")
			return -1
		self.generateEyeData(real_eyeList, landmarkList)
		for eye in real_eyeList:
			for pos in range(181):
				pass #insert weighting system here
	def generateEyeData(self, real_eyeList, landmarkList):
		#tricky, we need to use the hardware info from real_eyeList
		#plus the pose info from hypobot to transform our heading
		self.localEyeList = copy.deepcopy(real_eyeList) #gets the x, y, theta data
							#important that it be a deep copy, since each hbot really should have its own version of the data
		for eye in real_eyeList:
			i = eye.eyeNum
			#bird code call:
			#apply rotational matrix
			x = self.x + math.cos(self.theta)*eye.x_offset + math.sin(self.theta)*eye.y_offset
			y = self.y - math.sin(self.theta)*eye.x_offset + math.cos(self.theta)*eye.y_offset
			theta = self.theta + eye.theta_offset 
			array=range(181)
			for j in range(181):
				effective_theta = theta+j
				array[j] = calcIdealRange(x, y, effective_theta, landmarkList)
			self.localEyeList[i].IR = array
		print "generated a new eyeList for hypobot " + str(id(self)) + " at " + str((self.x, self.y, self.theta))

class weightHypobotListButton(button):
	def processClickDown(self, screen_pos):
		self.down = not self.down
		for hypobot in HypobotList:
			hypobot.changeWeight(eyeList)
		
class landmarkToggleButton(button):
	def processClickDown(self, screen_pos):
		self.down = not self.down

class eyeViewButton(button):
	eyeVisible=True
	def setup(self, eyeNum, eyeType, botView):
		if eyeType=="REAL":
			self.eyeVisible = botView.realEyeVisible[eyeNum]
		else:
			self.eyeVisible = botView.idealEyeVisible[eyeNum]
	def processClickDown(self, screen_pos):
		self.down = not self.down
		self.eyeVisible = self.down
	def processClickUp(self, screen_pos):
		pass

class startScanButton(button):
	serialWrapper = None
	def getSerialConnection(self, serialWrapper):
		self.serialWrapper=serialWrapper
	def processClickDown(self, screen_pos):
		self.down = True
		self.serialWrapper.orderScan()
	def processClickUp(self, screen_pos):
		self. down = False

class advanceSelectedHypobotButton(button):
	selectedHypobot=-1
	hypobotList = list()
	def takeHypobotSettings(self, selectedHypobot, hypobotList):
		self.selectedHypobot = selectedHypobot
		self.hypobotList = hypobotList
	def takeLandmarkList(self, landmarkList):
		self.localLandmarkList = landmarkList
	def takeEyeList(self, eyeList):
		self.localEyeList = eyeList
	def processClickDown(self, screen_pos):
		self.down = True
		if screen_pos[0] >= self.width/2:
			self.selectedHypobot += 1
		else:
			self.selectedHypobot -= 1
		if self.selectedHypobot >= len(self.hypobotList):
			self.selectedHypobot = 0
		if self.selectedHypobot < 0:
			self.selectedHypobot = len(self.hypobotList) - 1
		print(self.selectedHypobot)
		print(SelectedHypobot)
	def processClickUp(self, screen_pos):
		self. down = False
	def getSelectedHypobot(self):
		return self.selectedHypobot

class serialWrapper:
	def __init__(self):
		self.port = "/dev/ttyACM"
		self.baud = 115200
		self.connected = False
		self.ser = None
		self.readingWaiting = False
		self.readingList = list()
	def attemptConnect(self):
		done = False
		i=0
		while not (self.connected or done):
			tempPort = self.port + str(i)
			print("trying to connect to "+tempPort+ "...")
			try:
				self.ser = serial.Serial(tempPort, self.baud, timeout = 0.100)
				self.connected = True
				print("Yes! Connected to "+tempPort)
			except:
				print("...Nope!")
				i += 1
			if i > 30:
				print("no serial today, guy")
				done = True
				return -1
		while self.ser.inWaiting()>0:
			print(self.ser.read())
	def orderScan(self):
		self.ser.write("!")
		print("wrote '!'")
	def checkMessages(self):
		if not self.connected:
			return -1
		if self.ser.inWaiting() == 0:
			return -1
		else:
			x= self.ser.read()
			return x
	def update(self, eyeList):
		"""eyeList.clear()"""
		for reading in self.readingList:
			for eye in eyeList:
				eye.takeReading(reading)	
		pass
	def recordRange(self,eyeList):
		#time.sleep(0.02) #--build buffer, may be useless
		while self.ser.inWaiting() < 6:
			pass
		readout = list()
		for i in range (6):
			x = self.ser.read()
			readout.append(x)
		pos = ord(readout[0])
		IRlsb = ord(readout [1])
		IRmsb = ord(readout [2])
		USlsb = ord(readout[3])
		USmsb = ord(readout[4])	
		eyeNum = ord(readout[5])
		
		out = "readout: "
		for i in range(6):
			pass
			out +=repr(readout[i])
		print(out)
		
		IR = IRmsb*255 + IRlsb
		US = USmsb*255 + USlsb
		#print(pos)
		#print(eyeNum)
		Reading = reading(eyeNum, pos, IR, US)
		eyeList[eyeNum].IR[pos] = Reading.IR_feet
		eyeList[eyeNum].US[pos] = Reading.US_feet
		self.readingList.append(Reading)
		print ("eyeNum:", eyeNum, "pos", pos)
		if eyeNum == 1 and pos == 181:
			return True
		else:
			return False
		
			
class reading:
	IR_maxRange = 5 
	def __init__(self, eyeNum, pos, IR_raw, US_raw):
		self.pos = pos
		self.eyeNum = eyeNum
		self.IR_raw = IR_raw
		self.US_raw = US_raw
		if self.IR_raw != 0:
			self.IR_feet =  (2525.0*pow(IR_raw, - 0.85) - 4)/12
		else:
			self.IR_feet = 0
		self.IR_feet = min(self.IR_feet, self.IR_maxRange)
		self.US_feet = US_raw * 0.1

class eye:
	def __init__(self, eyeNum, x_offset, y_offset, theta_offset_in): #x and y offset are measured from center of bot.  Theta = 0 is bot's heading
		self.IR = [0.0]*181 #this is how you make a list of zeroes 181 long
		self.US = [0.0]*181
		self.x_offset=x_offset
		self.y_offset=y_offset
		self.theta_offset=theta_offset_in
		self.eyeNum = eyeNum
	def clear(self):
		IR = [0.0]*181
		US = [0.0]*181
	def takeReading(self, reading):
		if reading.eyeNum != self.eyeNum:
			print("Reading rejected")
			return
		else:
			self.IR[reading.pos] = reading.IR_feet
			self.US[reading.pos] = reading.US_feet
	def takeRange(self, IR_array, US_array):
		self.IR = IR_array
		self.US = US_array

			
		

	
""" --------------- setup: -----------------"""
#setup serial
SerialWrapper = serialWrapper()
SerialWrapper.attemptConnect()

#populate world with objects:
landmarkData=list()
"""  #approximate board coords:
landmarkData.append((1.44,8-0.894,"ROCK"))
landmarkData.append((1.96,8-2.98, "TREE"))
landmarkData.append((2.24,8-5.76, "TREE"))
landmarkData.append((4.02,8-6.96, "ROCK"))
landmarkData.append((4.07,8-3.03, "ROCK"))
landmarkData.append((6.24,8-1.74, "TREE"))
landmarkData.append((7.70,8-6.01, "TREE"))
"""  #my own test coords:
LandmarkList=list()
LandmarkList.append(landmark(3.0,3.0,"ROCK"))
LandmarkList.append(landmark(5.0,3.0,"TREE"))
LandmarkList.append(landmark(3.0,5.0,"TREE"))
LandmarkList.append(landmark(5.0,5.0,"ROCK"))

#make some hypobots
HypobotList = list()
for i in range (5):
	for j in range (5):
		HypobotList.append(hypobot(3.2+.4*i, 4.2+.4*j, 0)) #a buncha bots facing up
SelectedHypobot=0 #to help us keep track of which hypobot is selected

#assemble the robot:
EyeList = list()
EyeList.append(eye(0,  0.415,-0.415, -45.0))
EyeList.append(eye(1, -0.415,-0.415,  45.0))

for hypobot in HypobotList:
	hypobot.generateEyeData(EyeList, LandmarkList)

#figure out some

#initialize gui
H = 700
W = 1100
textHeight = 18

pygame.init()
pygame.font.init()
Font = pygame.font.Font(None, textHeight)
screen=pygame.display.set_mode((W,H),0,32)
screen.fill((127,127,127))
#set up frames:
BotView = botView(pygame, screen, 550, 30, 540, 540)
BoardView = boardView(pygame, screen, 5, 30, 540, 540, LandmarkList, EyeList)
BoardView.takeHypobotList(HypobotList, SelectedHypobot)
#buttons for BoardView:
LandmarkToggleButton = landmarkToggleButton(pygame, screen, 5, 5, 100, 20, "Show Landmarks", Font, True)
WeightHypobotListButton = weightHypobotListButton(pygame, screen, 110, 5, 100, 20, "Weight Hypobots", Font, True)
AdvanceSelectedHypobotButton = advanceSelectedHypobotButton(pygame, screen, 5, 575, 100, 20, "-/+", Font, True)
AdvanceSelectedHypobotButton.takeHypobotSettings(SelectedHypobot , HypobotList)
AdvanceSelectedHypobotButton.takeLandmarkList(LandmarkList)
#AdvanceSelectedHypobotButton.takeEyeList(EyeList)
#buttons for BotView:
StartScanButton = startScanButton(pygame, screen, 550, 5, 100, 20, "Scan", Font, False)
StartScanButton.getSerialConnection(SerialWrapper)
EyeViewButtonList = list()
for i in range(4):
	title = "R:"+str(i)
	butt = eyeViewButton(pygame,screen,550 + 25*i, 575, 20, 20, title, Font, True)
	butt.setup(i,"REAL", BotView)
	EyeViewButtonList.append(butt)
for i in range(4):
	title = "H:"+str(i)
	butt = eyeViewButton(pygame,screen,550 + 25*i, 600, 20, 20, title, Font, True)
	butt.setup(i,"IDEAL", BotView)
	EyeViewButtonList.append(butt)

frameList = []
for frame in (BotView, BoardView, LandmarkToggleButton, StartScanButton, WeightHypobotListButton, AdvanceSelectedHypobotButton): #IMPORTANT: IF YOU ADD A FRAME, PUT IT IN THIS LIST
	frameList.append(frame)
for butt in EyeViewButtonList:
	frameList.append(butt)

runNum = 0
newFrame = 0

for view in (BotView, BoardView):
	view.takeLandmarkList(LandmarkList)
	view.takeEyeList(EyeList)

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
	
	messageType = SerialWrapper.checkMessages()
	if messageType == 'C':
		pass
	if messageType == 'R':
		SerialWrapper.recordRange(EyeList)
		BotView.takeEyeList(EyeList)
		assert(BotView.localEyeList == EyeList)
		BotView.update()

	
	for view in (BotView, BoardView):
		view.takeEyeList(EyeList)
		view.takeHypobotList(HypobotList, SelectedHypobot)

	#EyeList[0].IR[0]=44

	SelectedHypobot = AdvanceSelectedHypobotButton.getSelectedHypobot() #ummm not sure why I need this but I do
	if newFrame == 0:
		for frame in frameList:
			frame.update()
		newFrame = 8
	newFrame -= 1
	"""
	BotView.update()
	BoardView.update()
	LandmarkToggleButton.update()
	StartScanButton.update()
	WeightHypobotListButton.update()
	"""
	pygame.display.update()
	#runNum -= 1
	
