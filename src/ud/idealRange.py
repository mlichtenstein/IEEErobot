import math
import landmark

def calcIdealRange(x_eye, y_eye, theta_board, landmarkList, speed): #theta_board is WRT board
	r = rangeLim
	theta_board = theta_board * math.pi/180  #math like this prefers to be done in radians
	circles = list()
	squares = list()
	radius = 0
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
			if speed == "SLOW":
				try:
					r = min(r,d*(math.cos(theta) - math.sqrt((radius/d)**2 - math.sin(theta)**2)))
				except:
					print("GAAAH!",x_eye, y_eye, theta, d)
			if speed == "ULTRAFAST":
				r = min(r,d - radius/2)
			if speed == "FAST":
				r = min(r, d - radius + radius*(theta/lim)**2)
	return r
