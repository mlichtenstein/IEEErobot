import cv2
import cv
import numpy
import math
import serial

#set up the serial
ard = serial.Serial('/dev/ttyACM0', 9600)
ard.write('90,0,90,f')

#circle detection sensitivity
canny_threshold = 20

#set up camera VideoCap(arg) might need to be 0 on panda
cap = cv2.VideoCapture(1)

cv2.namedWindow('test',1)

# show video on screen for testing
while True:
	flag, frame = cap.read()
	cv2.imshow('test', frame)
	ch = 0xFF & cv2.waitKey(1)
	if ch != 0xFF:
		break
src_gray = cv2.cvtColor( frame, cv.CV_BGR2GRAY )
src_gray = cv2.GaussianBlur( src_gray,(9,9), 2  )
#############################################################################
# old C++ circle detector
#
#cv2.HoughCircles( src_gray, circles, cv.CV_HOUGH_GRADIENT, 1, src_gray.rows/8, canny_threshold, 100, 0, 0 )
##############################################################################
print src_gray.shape
circles = cv2.HoughCircles( src_gray, cv.CV_HOUGH_GRADIENT,1, 30 , param1=canny_threshold, param2=100)

for cir in circles[0]:
	print cir
	somePointx = cv.Round(cir[0])
	somePointy = cv.Round(cir[1])
	radius = cv.Round(cir[2])
	cv2.circle( frame, (somePointx, somePointy), 3,(0,255,0), -1, 8, 0 )
	cv2.circle( frame, (somePointx, somePointy), radius, (0,0,255), 3, 8, 0 )
#else:
#	print "less than one circle detected"
cv2.namedWindow('farts', 1)
cv2.imshow('farts', frame)
cv2.waitKey(0)

#arm segment lengths (d = vertical offset)
a2 = 5 
a3 =7.85
d = 7.5

#scale view size src_gray.shape to physical area
#scaling factor = view size / inches of area 
x = (cir[0] - 113) / 28 
y = (261.8 - cir[1]) / 29.1
z = .45 #disk height offset

print "x = {0} y = {1}".format(x,y)

r = math.hypot(x,y)
s = z - d

theta1 = (math.atan2(y,x))*57.2957795
D = ((r*r) + (s*s) -(a2*a2) - (a3*a3))/(2*a2*a3)
theta3 = math.atan2(-math.sqrt(1 - D*D),D)
theta2 = math.atan2(s, r) -math.atan2(a3*math.sin(theta3), a2+a3*math.cos(theta3))
theta3 = -(theta3 * 57.2957795 )
theta2 = theta2 * 57.2957795 + 90

print  'theta1 = {0} theta2 = {1} theta3 = {2}'.format(theta1, theta2, theta3)
ard.write('{0},{1},{2},if'.format(int(theta1),int(theta2),int(theta3)))

while ard.inWaiting():
	pass

if ard.read() == 'd':
	ard.write('90,10,110,f')
	ard.flushInput()

while ard.inWaiting() == 0:
	pass

if ard.read() == 'd':
	ard.flushInput()

ard.write('240,10,110,f')

while ard.inWaiting() == 0:
	pass

if ard.read() == 'd':
	ard.flushInput()
	ard.write('90,0,90,of')
