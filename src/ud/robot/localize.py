"""
A library containing things critical to localization.  This defines
Eye, Hypobot, and HypobotCloud, and also contains idealRange functions
and a function for parsing the Arduino's scan report
"""

import math
import settings



def rawIRtoFeet(rawIR):
    if rawIR != 0:
        feet = (2525.0*pow(rawIR, - 0.85) - 4)/12
    else:
        feet = 0
    return feet

def rawUStoFeet(rawUS):
    if rawUS != 0:
        #temperature = settings.TEMPERATURE
        temperature = 20 # in celsius
        speedOfSound = (331.3+0.606 * temperature) * .0000032808399
        feet = speedOfSound * rawUS / 2
        return feet
    return 0

class Eye:
    def __init__(self, eyeNum, x_offset, y_offset, theta_offset,
                    dataPointNum, subtendedAngle):
        self.eyeNum = eyeNum
        self.x_offset=x_offset
        self.y_offset=y_offset
        self.theta_offset=theta_offset
        self.dataPointNum = dataPointNum
        self.IR = [0.0]*(dataPointNum+1)
        self.US = [0.0]*(dataPointNum+1)
        self.thetaList = list() #a list of the theta at which each measurement occurs
        for i in range(self.dataPointNum):
            self.thetaList.append(float(self.theta_offset) + float(i)/(dataPointNum-1) * subtendedAngle)    
    def clear(self):
        IR = [0.0]*self.dataPointNum
        US = [0.0]*self.dataPointNum
    def takeReading(self, dataPoint, IR, US):
        self.IR[dataPoint] = IR
        self.US[dataPoint] = US
    def printReading(self):
        for range in self.IR:
            print ("Eye "+str(self.eyeNum)+" sees  an IR range of " + str(range))

def messageTupleToEyeList(messageTuple):
    string = messageTuple[2]
    dataPointStringList = string.split('|')[1:]
    import world
    import copy
    eyeList = copy.deepcopy(world.World().eyeList)
    for dataPointString in dataPointStringList:
        dataPoint = dataPointString.split(',')
        eyeNum = int(dataPoint[0])                                  
        dataPointNum = int(dataPoint[1])
        IRlsb = int(dataPoint[2])
        IRmsb = int(dataPoint[3])           
        USlsb = int(dataPoint[4])
        USmsb = int(dataPoint[5])
        rawIR = IRmsb*256 + IRlsb
        rawUS = USmsb*256 + USlsb
        IR = rawIRtoFeet(rawIR)
        US = rawUStoFeet(rawUS)
        #print("Mt2el: Eye "+str(eyeNum)+" reports IR="+str(IR)+" feet at data point "+str(dataPointNum))
        eyeList[eyeNum].takeReading(dataPointNum,IR,US)
    return eyeList


class Hypobot:
    def __init__(self, x, y, theta):
        import robotbasics
        self.x = x
        self.y = y
        self.theta = theta
        self.pose = robotbasics.Pose(x,y,theta)
        self.localEyeList = list()
        self.weight = 1
        import random
        self.red = random.random() * 256
        self.blue = random.random() *256
        self.green = random.random() *256
        self.color = (int(self.red),int(self.green), int(self.blue))
    def changeWeight(self, real_eyeList, landmarkList):
        """
        this method weights each hypobot according to how well it's
        generated eye data resembles the real eye data.  It's more or
        less a simple product of beysian probabilities--a monte carlo
        kalman filter.  ONLY call it after you've generated eye data,
        or else it will think the robot is in a rock or something.
        
        Params:
        real_eyeList is the actual data from the bot.
        landmarkList is a list of landmark objects to consider.  It could
        concievably be a shortened list.
        """
        if len(real_eyeList)!= len(self.localEyeList):
            print("eyeList mismatch!")
            return -1
        self.weight = 1
        for eyeNum in range(0,len(self.localEyeList)):
            distSum = 0
            for i in range(settings.SCAN_DATA_POINTS):
                distance = 10
                correctionWindow = 2
                for j in range(max(0,i-correctionWindow),min(settings.SCAN_DATA_POINTS,i+correctionWindow+1)):
                    a = self.localEyeList[eyeNum].IR[i]
                    b =  real_eyeList[eyeNum].IR[j]
                    #distance = min(distance, (a**2 + b**2 - 2*a*b*math.cos((i-j)*math.pi/180))) #SLOW
                    distance = min(distance, abs(a-b))  #FAST
                self.weight *= math.exp((-(distance)**2)*.008)
        self.color = (  int(self.weight*self.red),
                        int(self.weight*self.green),
                        int(self.weight*self.blue))
    def generateEyeData(self, landmarkList):
        #tricky, we need to use the hardware info from real_eyeList
        #plus the pose info from hypobot to transform our heading
        import copy
        import world
        self.localEyeList = copy.deepcopy(world.World().eyeList) #gets the x, y, theta data
        #important that it be a deep copy, since each hbot really should have its own version of the data
        for eye in self.localEyeList:
            #apply rotational matrix
            x = self.x + math.cos(self.theta)*eye.x_offset + math.sin(self.theta)*eye.y_offset
            y = self.y - math.sin(self.theta)*eye.x_offset + math.cos(self.theta)*eye.y_offset
            theta = self.theta + eye.theta_offset 
            for j in range(settings.SCAN_DATA_POINTS):
                effective_theta = eye.thetaList[j]
                #----------------------change generation speed here ---------------------
                eye.IR[j] = calcIdealRange(x, y, effective_theta, landmarkList, "SLOW")

           
class HypobotCloud:
    """
    This class is a wrapper for hypobotList.  It includes functions for
    weighting, generating new hypobots, generating data for the hypobots,
    normalizing the wieghts, and pruning low-weight hbots.

    NOTE:  generating eye data is a hefty operation.
    generating data for 100 hbots takes about 3 seconds.  Perform this operation
    while the scan is going on.  Weighting is also hefty.  Weighting 100
    hbots takes about 1 second.  For this reason, weighting and generating
    data are NOT performed by any other function, so generateEyeData()
    and weight() must both be called explicitly.
    Do it like this:
    1) generate your bots
    2) start scan
    3) generate eye data
    4) get the scan's results
    5) weight
    6) normalize
    7) prune
    """
    def __init__(self):
        self.hypobotList = list()
    def clear(self):
        l = len(self.hypobotList)
        self.hypobotList = list()
        print("deleted " + str(l) + " hypobots.  No hypobots left.")
    def count(self):
        return len(self.hypobotList)
    def appendBloom(self, multiplier, poseSigma):
        import random
        import copy
        appended = 0
        bloomEnd = len(self.hypobotList)
        for index in range(0,bloomEnd):
            for i in range(0,multiplier):
                pose = self.hypobotList[index].pose
                x = random.gauss(pose.x, poseSigma.x)
                y = random.gauss(pose.y, poseSigma.y)                    
                theta = pose.theta + random.gauss(pose.theta, poseSigma.theta)
                if x>.5 and x<7.5 and y>.5 and y<7.5:
                    self.hypobotList.append(Hypobot(x,y,theta))
                    appended +=1
        print("Bloomed "+str(appended)+" hbots.")
    def appendGaussianCloud(self, cloudSize, pose, poseSigma):
        import random 
        for i in range (0,cloudSize):
            while 1:
                x = random.gauss(pose.x, poseSigma.x)
                y = random.gauss(pose.y, poseSigma.y)
                if x>.5 and x<7.5 and y>.5 and y<7.5:
                    break
            theta = random.gauss(pose.theta, poseSigma.theta)
            self.hypobotList.append(Hypobot(x,y,theta))
        print("Added "+str(cloudSize)+" in a gaussian about "+
                str(pose.x)+','+str(pose.y)+','+str(pose.theta))
    def appendBlanket(self, cloudRootSize, theta):
        #blankets the field with cloudRootSize*CloudRootSize hypobots
        l = 7/(cloudRootSize - 1)
        for i in range(0,cloudRootSize):
            for j in range(0,cloudRootSize):
                self.hypobotList.append(Hypobot(.5 + l*i, .5+l*j, theta))
    def generateEyeData(self, landmarkList):
        for hypobot in self.hypobotList:
            hypobot.generateEyeData(landmarkList)
        print("generated eye data for "+str(len(self.hypobotList))+" hbots.")
    def weight(self, real_eyeList, landmarkList):
        for hypobot in self.hypobotList:
            hypobot.changeWeight(real_eyeList, landmarkList)
        print ("reweighted "+str(len(self.hypobotList))+" hbots.")
    def normalizeWeights(self):
        #this method scales the weights so the lowest is 0 and the highest is 1
        #go through the hypbobots
        minWeight = 1
        maxWeight = 0
        for hypobot in self.hypobotList:
            minWeight = min(minWeight, hypobot.weight)
            maxWeight = max(maxWeight, hypobot.weight)
        #adjust the weights to span from 0 to 1
        if minWeight == maxWeight:
            print("All your hbots have the same weight!  Something is wrong.")
            return
        for i in range(len(self.hypobotList)):
            hypobot = self.hypobotList[i]
            hypobot.weight = (hypobot.weight - minWeight)/(maxWeight-minWeight)
    def collapse(self, threshold):
        import robotbasics
        #this method collapses the "wavefunction", averaging over all weights above threshold
        #threshold of .5 seems to work well
        self.normalizeWeights()
        #do a weighted average:
        avg = robotbasics.Pose(0,0,0)
        totWeight = 0
        for hypobot in self.hypobotList:
            if hypobot.weight > threshold:
                avg.x += hypobot.x * hypobot.weight
                avg.y += hypobot.y * hypobot.weight
                avg.theta += hypobot.theta * hypobot.weight
                totWeight += hypobot.weight
        avg.x /= totWeight
        avg.y /= totWeight
        avg.theta /= totWeight
        return avg
    def prune(self, threshold):
        #this method cuts all weights that are below threshold
        deleted = 0
        self.normalizeWeights()
        for hypobot in self.hypobotList:
            if hypobot.weight < threshold:
                deleted += 1
                self.hypobotList.remove(hypobot)
        print("Pruned "+str(deleted)+" hypobots. "+
                str(len(self.hypobotList))+" remain.")



def calcIdealRange(x_eye, y_eye, theta_board, landmarkList, speed): #theta_board is WRT board
    """
    This function will calculate the range detected by an ideal IR
    sensor    at x_eye, y_eye and pointing in the theta_board direction.
    Speed refers to the speed of the calculations.  It demands a string,
    which can be one of 3 options:

    "SLOW":  Dead-on ideal (for rocks, but not for trees...eh)
        this is not recommended, it takes 10-100 times longer than the others
    "FAST":  Recommended--it calculates the ranges as parabolas, which
        is a decent approximation in good time
    "ULTRAFAST": It calculates the ranges as flat fans, which is a dirty
        approx but is about half again as fast as FAST.  recommended only
        in the case of a very lost robot that is blanketing the field
        with thousands of hbots.  God help us if this happens.
    """
    import world
    r = settings.SCAN_IR_RANGELIM #caps ideal ranges
    theta_board = theta_board * math.pi/180  #math like this prefers to be done in radians
    circles = list()
    squares = list()
    radius = 0
    side = 0
    for landmark in landmarkList:
        if landmark.landmarkType=="ROCK":
            circles.append((landmark.x, landmark.y, world.World().rockRadius))
        else:
            #change to squares.append if you implement special handling for squares
            #0.7071 = sqrt(2)/2
            circles.append((landmark.x, landmark.y, world.World().treeSide * 0.7071))
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
                    print("GAAAH! Imaginary range!  Something is wrong\
                            in calcIdealRange",x_eye, y_eye, theta, d)
            if speed == "ULTRAFAST":
                r = min(r,d - radius/2)
            if speed == "FAST":
                r = min(r, d - radius + radius*(theta/lim)**2)
    return r