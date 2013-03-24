#robotbasics.py

class WorldConst:
    robotWidth = .95
    
worldConst = WorldConst()

class Pose:
    x=0
    y=0
    theta=0
    def __init__(self,x,y,theta):
        self.setPose(x,y,theta)
    def setPose (self,x,y,theta):
        self.x = x
        self.y = y
        self.theta = theta

class State:
    #The robot's internal state variables go here:
    def __init__(self):
        pass
    mode = None
    moving = False
    pose = Pose(0,0,0)
    poseUncertainty = Pose(0,0,0)
    pitch = 0.0
    roll = 0.0
    distanceSinceScan = Pose(0,0,0) #distance, in feet, since last scan
    motorConfig = [0,0,0,0] #the thetas of each wheel servo
    motorPWM = 0, 0 #the duty cycle of the PWM output to each motor
    armConfig = [0,0,0] #the thetas of each arm servo
    #hypobotCloud = HypobotCloud()
    eyeSet = []
    remainingPucks = (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16)
    magnetOn = False
    lightsOn = False

class Eye:
    def __init__(self, eyeNum, x_offset, y_offset, theta_offset,
                    dataPointNum, subtendedAngle):
        self.dataPointNum = dataPointNum
        self.IR = [0.0]*dataPointNum
        self.US = [0.0]*dataPointNum
        self.x_offset=x_offset
        self.y_offset=y_offset
        self.theta_offset=theta_offset
        self.eyeNum = eyeNum
        self.dataPointNum = dataPointNum_in
        self.subtendedAngle = subtendedAngle_in
        self.thetaList = list() #a list of the theta at which each measurement occurs
        for i in range(self.dataPointNum):
            self.thetaList.append(float(self.theta_offset) - float(i)/dataPointNum * subtendedAngle)    
    def clear(self):
        IR = [0.0]*self.dataPointNum
        US = [0.0]*self.dataPointNum
    def takeReading(self, dataPoint, IR, US):
        pass
    def takeRange(self, IR_array, US_array):
        self.IR = IR_array
        self.US = US_array

class Hypobot(Pose):
    localEyeList = list()
    def changeWeight(self, real_eyeList, landmarkList):
        if len(real_eyeList)!= len(self.localEyeList):
            print("eyeList mismatch!")
            return -1
        self.generateEyeData(real_eyeList, landmarkList)
        print id(self.localEyeList)
        self.weight = 1
        """#original weight function:
        for eye in real_eyeList:
            for i in range(181):
                for j in range(max(0,i-0),min(181,i+0+1)):
                    a = eye.IR[i]
                    b =  self.localEyeList[eye.eyeNum].IR[j]
                    self.weight *= math.exp((-(a-b)**2)*.001)
                #print self.localEyeList[eye.eyeNum].IR[pos]
                pass"""
        """#Matt + max hybrid:"""
        for eye in real_eyeList:
            distSum = 0
            for i in range(dataPointNum):
                distance = 10
                correctionWindow = 2
                for j in range(max(0,i-correctionWindow),min(dataPointNum,i+correctionWindow+1)):
                    a = eye.IR[i]
                    b =  self.localEyeList[eye.eyeNum].IR[j]
                    #distance = min(distance, (a**2 + b**2 - 2*a*b*math.cos((i-j)*math.pi/180))) #SLOW
                    distance = min(distance, abs(a-b))  #FAST
                #print("eer", ,eyeNum, i, distSum)
                self.weight *= math.exp((-(distance)**2)*.008)
        
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
            array=range(dataPointNum)
            for j in range(dataPointNum):
                effective_theta = eye.thetaList[j]
                #----------------------change speed here ---------------------
                array[j] = calcIdealRange(x, y, effective_theta, landmarkList, "SLOW")
            self.localEyeList[i].IR = array
        #print "generated a new eyeList for hypobot " + str(id(self)) + " at " + str((self.x, self.y, self.theta))
