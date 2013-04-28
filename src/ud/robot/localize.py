"""
A library containing things critical to localization.  This defines
Eye, Hypobot, and HypobotCloud, and also contains idealRange functions
and a function for parsing the Arduino's scan report
"""

import math
import sys
sys.path.append("..")
import settings


def rawIRtoFeet(rawIR):
    if rawIR != 0:
        feet = (2525.0*pow(rawIR, - 0.85) - 4)/12
    else:
        feet = 0
    return feet


def feetToRawIR(dInFeet):
    #using a lookup table.  Sue me.  --Max
    table=((4, 444.1666666667),(5, 490.1666666667),(6, 561),
            (7, 560.5),(8, 547.1666666667),(9, 522.1666666667),(10, 493.8333333333),(11, 459.8333333333),
            (12, 424.3333333333),(13, 402.5),(14, 382.6666666667),(15, 346.8333333333),(16, 328.8333333333),
            (17, 301.5),(18, 291.5),(19, 281.1666666667),(20, 257.6666666667),(21, 249),(22, 232),
            (23, 226.1666666667),(24, 211),(25, 203),(26, 200.3333333333),(27, 200.8333333333),
            (28, 191.6666666667),(29, 196.8333333333),(30, 188.1666666667),(31, 190.3333333333),
            (32, 184),(33, 185.1666666667),(34, 186.6666666667),(35, 183.3333333333),(36, 186.6666666667),
            (37, 178),(38, 178),(39, 181.1666666667),(40, 182.1666666667),(41, 183.5),(42, 182.5),
            (43, 179.6666666667),(44, 178.1666666667),(45, 176.6666666667),(46, 171.3333333333),(47, 176.3333333333),
            (48, 182.6666666667),(49, 173.1666666667),(50, 170.1666666667),(51, 166.3333333333),(52, 176.8333333333),
            (53, 172.3333333333),(54, 172.8333333333),(55, 167.5),(56, 168),(57, 173.3333333333),(58, 172.5),
            (59, 167.6666666667),(60, 163.3333333333),(61, 172.5))
    d = float(dInFeet)*12 #in inches
    if d >= 4 and d <60:
        lower = int(d)
        upper = lower+1
        interval = d - lower
        interpolated = table[lower-4][1]*(1-interval) + table[upper-4][1]*(interval) #the 0th entry corresponds to 4 inches
        return interpolated
    elif d >= 60:
        return 180
    else:
        return 0

def rawUStoFeet(rawUS):
    if rawUS != 0:
        #temperature = settings.TEMPERATURE
        temperature = 20 # in celsius
        speedOfSound = (331.3+0.606 * temperature) * .0000032808399
        feet = speedOfSound * rawUS / 2
        return feet
    return 0

"""
Class Eye represents the Eye Module. You pass the relevant eye in as eyenum. X_offset and y_offset are used to find the distance from the
center of the robot. It is the container to store and manipulate readings from the IR and US Sensors.

"""

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
        if eyeNum == 0 or eyeNum == 2: #clockwise
            for i in range(self.dataPointNum):
                self.thetaList.append(float(self.theta_offset)
                 - float(i)/(dataPointNum-1) * subtendedAngle)    
        else:
            for j in range(self.dataPointNum):
                i=self.dataPointNum - j - 1
                self.thetaList.append(float(self.theta_offset)
                 - float(i)/(dataPointNum-1) * subtendedAngle)
    def clear(self):
        IR = [0.0]*self.dataPointNum
        US = [0.0]*self.dataPointNum
    def takeReading(self, dataPoint, IR, US):
        """
        takeReading returns data from both the Infrared sensor and the Ultrasound sensor
        """    
        self.IR[dataPoint] = IR
        self.US[dataPoint] = US
    def printReading(self):
        for range in self.IR:
            print "Eye",self.eyeNum,"sees  an IR range of",range

def messageTupleToEyeList(messageTuple):
    """
    messageTupleToEyelist receives data from the arduino and processes it to be handled by the pandaboard
    """
    string = messageTuple[2]
    dataPointStringList = string.split('|')[1:]
    import world
    import copy
    eyeList = copy.deepcopy(world.World().eyeList)
    for dataPointString in dataPointStringList:
        dataPoint = dataPointString.split(',')
        try:
            eyeNum = int(dataPoint[0])                                  
            dataPointNum = int(dataPoint[1])
            IRlsb = int(dataPoint[2])
            IRmsb = int(dataPoint[3])           
            USlsb = int(dataPoint[4])
            USmsb = int(dataPoint[5])
            rawIR = IRmsb*256 + IRlsb
            rawUS = USmsb*256 + USlsb
            US = rawUStoFeet(rawUS)  #this is weird--Eye stores raw IR data but converted US data.  So sorry.
            eyeList[eyeNum].takeReading(dataPointNum,rawIR,US)
        except Exception as error:
            print "At least one data point was lost.",error
    return eyeList

"""
Hypobot generates a cloud of hypothetical bots for statistical comparison of incoming data to find its likeliest current location.
The closest number of hypobots that exist are averaged to a final value. The number is stored in modes.pi. It's declared in the localize function.
"""
class Hypobot:
    """
    Weight:
    According to Beyes theorem, each measurement tells you something about the correctness of a hypobot. The weight
    starts at 1 and is reduced by a gaussian factor for each sensor measurement. (Kalman Filter)
    """
    def __init__(self, x, y, theta, weight = 1):
        import robotbasics
        self.scootAngleSigma = 2
        self.scootDistanceSigma = 0.1
        self.rotateSigma = 2 
        self.pose = robotbasics.Pose(x,y,theta)
        self.localEyeList = list()
        self.weight = weight
        self.weightForgiveness = 1/10
        import random
        self.red = random.random() * 256
        self.blue = random.random() *256
        self.green = random.random() *256
        self.color = (int(self.red),int(self.green), int(self.blue))
    def string(self):
        return self.pose.string()+" with weight "+str(self.weight)
    def changeWeight(self, real_eyeList, landmarkList):
        """
        this method weights each hypobot according to how well its 
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
        logWeight = 0
        for eyeNum in range(0,len(self.localEyeList)):
            distSum = 0
            for i in range(settings.SCAN_DATA_POINTS):
                #first do IR:
                if real_eyeList[eyeNum].IR[i] != 0:     
                    a = self.localEyeList[eyeNum].IR[i]
                    b =  real_eyeList[eyeNum].IR[i]
                    #print a,"=ir=", b
                    distance = abs(a-b)  #FAST
                    logWeight += -(distance/self.weightingSigmaIR(a)/2)**2
                    #^Gaussian function of approximation for computing weight of a measurement."
                #Next do US
                if real_eyeList[eyeNum].US[i] != 0 and real_eyeList[eyeNum].US[i] < 1.0:
                    a = self.localEyeList[eyeNum].US[i]
                    b =  real_eyeList[eyeNum].US[i]
                    distance = abs(a-b)  #FAST
                    #print a,"=us=", b
                    logWeight += -(distance/self.weightingSigmaUS(a)/2)**2
        self.weight = math.exp(logWeight)

    def weightingSigmaIR(self, IRrange):
        #finding sigma in a method allows it to be non-constant, making this an Extended Kalman Filter
            return 100
    def weightingSigmaUS(self, USrange):
        return 10.0/12 #tenth of an inch?  Heh, maybe
    def generateEyeData(self, landmarkList):
        """
        generateEyeData() gives calculated values of what each hypobot would be seeing based on its x,y,and theta.
        """
        #tricky, we need to use the hardware info from real_eyeList
        #plus the pose info from hypobot to transform our heading
        import copy
        import world
        self.localEyeList = copy.deepcopy(world.World().eyeList) #gets the x, y, theta data
        #important that it be a deep copy, since each hbot really should have its own version of the data
        for eye in self.localEyeList:
            #apply rotational matrix
            x = self.pose.x + math.cos(self.pose.theta)*eye.x_offset + math.sin(self.pose.theta)*eye.y_offset
            y = self.pose.y - math.sin(self.pose.theta)*eye.x_offset + math.cos(self.pose.theta)*eye.y_offset
            theta = self.pose.theta + eye.theta_offset 
            for j in range(settings.SCAN_DATA_POINTS):
                effective_theta = self.pose.theta + eye.thetaList[j]
                #----------------------change generation speed here ---------------------
                distInFeetIR = calcIdealRangeIR(x, y, effective_theta, landmarkList, "FAST")
                eye.IR[j] = feetToRawIR(distInFeetIR)
                distInFeetUS = calcIdealRangeUS(x, y, effective_theta, landmarkList)
    def scootHypobot(self, scootDistance, scootAngle):
        import random
        import robotbasics
        thetaEff = (self.pose.theta + random.gauss(scootAngle, self.scootAngleSigma))*math.pi/180
        dEff = random.gauss(scootDistance,self.scootDistanceSigma)
        newPose = robotbasics.Pose(
                        self.pose.x + dEff*math.cos(thetaEff),
                        self.pose.y - dEff*math.sin(thetaEff),
                        self.pose.theta)
        self.pose = newPose
    def rotateHypobot(self,rotateAngle):
        import random
        newTheta = self.pose.theta + random.gauss(rotateAngle, self.rotateSigma)
        self.pose.theta = newTheta
    """
    DetectCollision is used to kill off any hypobot that is colliding with another object
    """
    def detectCollision(self):
        import world
        s = world.World().robotSide/2
        if self.pose.x < 0.4 or self.pose.x > 7.6 or self.pose.y < 0.4 or self.pose.y > 7.6:
            return True
        for landmark in world.World().landmarkList:
            dsquared = (self.pose.x-landmark.x)**2 + (self.pose.y-landmark.y)**2
            if dsquared < (landmark.effRadius + s)**2:
                return True
        x = self.pose.x
        y = self.pose.y
        theta = self.pose.theta
        xa = s*math.cos(self.pose.theta*math.pi/180)
        ya = s*math.sin(self.pose.theta*math.pi/180)
        xb = s*math.sin(self.pose.theta*math.pi/180)
        yb = s*math.cos(self.pose.theta*math.pi/180)
        cornerList = [  (x-xa+xb,y+ya+yb),
                        (x-xa-xb,y+ya-yb),
                        (x+xa-xb,y-ya-yb),
                        (x+xa+xb,y-ya+yb) ]
        for corner in cornerList:
            for landmark in world.World().landmarkList:
                dsquared = (corner[0]-landmark.x)**2 + (corner[1]-landmark.y)**2
                if dsquared < landmark.effRadius**2:
                    return True
            if corner[0]<-.1 or corner[0]>8.1 or corner[1]<-0.1 or corner[1]>8.1:
                return True

        return False
        """
        
        else:
            return False
        """

        
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
    def __init__(self, cloudSize):
        self.hypobotList = list()
        self.cloudSize = cloudSize #approx size of cloud--we will bloom and prune to stay near this
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
                weight = self.hypobotList[index].weight
                x = random.gauss(pose.x, poseSigma.x)
                y = random.gauss(pose.y, poseSigma.y)                    
                theta = random.gauss(pose.theta, poseSigma.theta)
                if x>.5 and x<7.5 and y>.5 and y<7.5:
                    self.hypobotList.append(Hypobot(x,y,theta,weight))
                    appended +=1
        print("Bloomed "+str(appended)+" hbots.")
        self.flatten()
    def resampleOne(self):
        #like appendBoost but no sigma
        import random
        while True:
            cloneTarget = self.hypobotList[int(random.random()*len(self.hypobotList))]
            #if cloneTarget.weight > random.random(): 
            if True:
                clone = cloneTarget
                break
        self.hypobotList.append(clone)
    def resampleOneWithGaussian(self, poseSigma):
        import random
        clone = Hypobot(0,0,0,1)
        while True:
            cloneTarget = self.hypobotList[int(random.random()*len(self.hypobotList))]
            #if cloneTarget.weight > random.random():
            if True:
                clone = Hypobot(random.gauss(cloneTarget.pose.x, poseSigma.x),
                            random.gauss(cloneTarget.pose.y, poseSigma.y),
                            random.gauss(cloneTarget.pose.theta, poseSigma.theta),
                            cloneTarget.weight)
                if clone.detectCollision() == False:
                    break
        #print "appended:",clone.string()
        self.hypobotList.append(clone)
    def appendFlatSquare(self, cloudSize, centerPose, xyside, thetaside):
        #makes a statistically flat square  of hbots centered around centerpose with sides defined by edgePose
        import random
        for i in range(0,cloudSize):
            x = random.uniform(centerPose.x-xyside/2,centerPose.x+xyside/2)
            y = random.uniform(centerPose.y-xyside/2,centerPose.y+xyside/2)
            theta = random.uniform(centerPose.theta-thetaside/2,centerPose.theta+thetaside/2)
            self.hypobotList.append(Hypobot(x,y,theta))
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
    def flatten(self):
        for hbot in self.hypobotList:
            hbot.weight = 1
    def clearCollided(self):
        deleted = 0
        killList = list()
        for hbot in self.hypobotList:
            if hbot.detectCollision() == True:
                killList.append(hbot)
                deleted += 1
        print "average hbot is ",self.average().string()
        for hbot in killList:
            self.hypobotList.remove(hbot)
        print "Deleted",deleted,"hbots due to collisions.",len(self.hypobotList),"remain."
    def generateEyeData(self, landmarkList):
        print "Generating eye data..."
        import time
        startTime = time.time()
        for hypobot in self.hypobotList:
            hypobot.generateEyeData(landmarkList)
        ti = "%.2f" % (time.time()-startTime)
        print"Generated eye data for",len(self.hypobotList),"hbots in",ti,"seconds."
    def weight(self, real_eyeList, landmarkList):
        import time
        startTime = time.time()
        for hypobot in self.hypobotList:
            hypobot.changeWeight(real_eyeList, landmarkList)
        ti = "%.2f" % (time.time()-startTime)
        print"Weighted",len(self.hypobotList),"hbots in",ti,"seconds."
    def normalize(self):
        #this method adjusts the weights so their total is 1.  Returns peak hbot
        #go through the hypbobots
        totWeight = 0.0
        peakWeight = 0.0
        peakBot = Hypobot(-1,-1,0, 1)
        for hypobot in self.hypobotList:
            totWeight += hypobot.weight
        if totWeight == 0:
            print "TOTAL WEIGHT IS ZERO, DANGER"
        for i in range(0,len(self.hypobotList)):
            if hypobot.weight > 1 or hypobot.weight == 0: #NOTE:  This is an ugly workaround....please fix me later!
                self.hypobotList.remove(hypobot)
            else:
                hypobot = self.hypobotList[i]
                oldWeight = hypobot.weight
                hypobot.weight /= totWeight
                #print "for hbot number",i,"new,old =",oldWeight,hypobot.weight
                if peakWeight < hypobot.weight:
                    peakWeight = max(peakWeight, hypobot.weight)
                    peakBot = hypobot
        totWeight = 0
        for hypobot in self.hypobotList:
            totWeight += hypobot.weight
        print ("Normalized cloud.  Peak hbot is at " + str(peakBot.pose.x)
                +", "+str(peakBot.pose.y)+", "+str(peakBot.pose.theta)
                +" with weight " + str(peakBot.weight))
        print ("Total weight is now",totWeight)
    def getPeakBot(self):
        peakWeight = 0
        retBot = Hypobot(-1,-1,0, -1)
        for hbot in self.hypobotList:
            if hbot.weight > peakWeight:
                peakWeight = hbot.weight
                retBot = hbot
        if retBot.weight<0:
            print "All hbot weights are zero. Probably your class Hypobot weightingSigma is too low."
        return retBot
    def peakWeight(self):
        return self.getPeakBot().weight
    def average(self):
        import robotbasics
        #this method collapses the "wavefunction", averaging over all weights above threshold
        #threshold of .5 seems to work well
        #do a weighted average:
        avg = robotbasics.Pose(0,0,0)
        totWeight = 0
        for hypobot in self.hypobotList:
            avg.x += hypobot.pose.x * hypobot.weight
            avg.y += hypobot.pose.y * hypobot.weight
            avg.theta += hypobot.pose.theta * hypobot.weight
            totWeight += hypobot.weight
        self.totWeight=totWeight
        try:
            avg.x /= totWeight
            avg.y /= totWeight
            avg.theta /= totWeight
        except:
            print "Total weight is zero.  Probably, something is wrong with your eye modules"
        return avg
    def stdDev(self,average):
        """
        stdDev() is meant to be called after average() and normalize,
         otherwise self.average will be wrong or the weights won't make
         sense
        """
        import robotbasics
        import math
        stdDev = robotbasics.Pose(0,0,0)
        for hbot in self.hypobotList:
            stdDev.x += (hbot.pose.x - average.x)**2*hbot.weight
            stdDev.y += (hbot.pose.y - average.y)**2*hbot.weight
            stdDev.theta += (hbot.pose.theta - average.theta)**2*hbot.weight
        stdDev.x = math.sqrt(stdDev.x)
        stdDev.y = math.sqrt(stdDev.y)
        stdDev.theta = math.sqrt(stdDev.theta)
        return stdDev
    def pruneThreshold(self, threshold):
        #this method cuts all weights that are below threshold
        deleted = 0
        for hypobot in self.hypobotList:
            if hypobot.weight < threshold:
                deleted += 1
                self.hypobotList.remove(hypobot)
        print("Pruned "+str(deleted)+" hypobots with weights less than "
            +str(threshold)+".")
        print(str(len(self.hypobotList))+" hbots remain.")
    def pruneFraction(self, fraction):
        #this method prunes the lowest hypobots, so fraction = .9 means only the top 10% remain
        toPrune = int(len(self.hypobotList)*fraction)  
        killList = sorted(self.hypobotList, key = lambda hbot: hbot.weight)
        for i in range(0,toPrune):
            self.hypobotList.remove(killList[i])
    def describeCloud(self):
        print "========HypobotCloud Report:============="
        print "The cloud has ",len(self.hypobotList)," hbots."
        print ("The max weight is "
                +str(max(self.hypobotList,key=lambda hbot: hbot.weight).weight)
                +" and the min weight is "
                +str(min(self.hypobotList,key=lambda hbot: hbot.weight).weight))
        avg = self.average()
        print "The average hypobot is at", avg.string()
        stdDev = self.stdDev(avg)
        print "The standard deviation is", stdDev.string()
        print "========================================="
    def scootAll(self, distance, angle):
        for hbot in self.hypobotList:
            hbot.scootHypobot(distance,angle)
    def rotateAll(self, angle):
        for hbot in self.hypobotList:
            hbot.rotateHypobot(angle)

def calcIdealRangeIR(x_eye, y_eye, theta_board, landmarkList, speed): #theta_board is WRT board
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
    r = 100 #caps ideal ranges
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

def calcIdealRangeUS(x_eye, y_eye, theta_board, landmarkList):
    import world
    r = 100 #start with that range
    for landmark in landmarkList:
        if landmark.landmarkType == "ROCK":
            d = math.sqrt((x_eye-landmark.x)**2 + (y_eye-landmark.y)**2) - world.World().rockRadius
            r = min(r,d)
        if landmark.landmarkType == "TREE":
            #treeSide = world.World().treeSide
            treeSide = 2
            if x_eye < landmark.x + treeSide/2 and x_eye > landmark.x - treeSide/2:
                d = abs(y_eye - landmark.y) - treeSide/2
            elif y_eye < landmark.y + treeSide/2 and y_eye > landmark.y - treeSide/2:
                d = abs(x_eye - landmark.x) - treeSide/2
            else:
                x_corner = landmark.x + math.copysign(treeSide/2, x_eye - landmark.x)
                y_corner = landmark.y + math.copysign(treeSide/2, y_eye - landmark.y)
                d = math.sqrt((x_eye-x_corner)**2 + (y_eye-y_corner)**2)
            r = min(r,d)
    return r

if __name__ == "__main__":

    import robotbasics
    print calcIdealRangeUS(0,6.5/12,222,[robotbasics.Landmark(0.0,0, "ROCK")])

    if __name__ == "__main__":
        from robotbasics import *
        hCloud = HypobotCloud(10)
        hCloud.appendGaussianCloud(hCloud.cloudSize, Pose(4,4,0), Pose(.5,.5,10))
        hCloud.normalize()
        for hbot in hCloud.hypobotList:
            print hbot.string()
        hCloud.describeCloud()    
        hCloud.scootAll(1,0)
        for hbot in hCloud.hypobotList:
            print hbot.string()
        hCloud.describeCloud()
