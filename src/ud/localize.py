class Eye:
    def __init__(self, eyeNum, x_offset, y_offset, theta_offset,
                    dataPointNum, subtendedAngle):
        self.eyeNum = eyeNum
        self.x_offset=x_offset
        self.y_offset=y_offset
        self.theta_offset=theta_offset
        self.dataPointNum = dataPointNum
        self.IR = [0.0]*dataPointNum
        self.US = [0.0]*dataPointNum
        self.thetaList = list() #a list of the theta at which each measurement occurs
        for i in range(self.dataPointNum):
            self.thetaList.append(float(self.theta_offset) - float(i)/(dataPointNum-1) * subtendedAngle)    
    def clear(self):
        IR = [0.0]*self.dataPointNum
        US = [0.0]*self.dataPointNum
    def takeReading(self, dataPoint, IR, US):
        pass
    def takeRange(self, IR_array, US_array):
        self.IR = IR_array
        self.US = US_array

class Hypobot:
    def __init__(self, x, y, theta):
        import robotbasics
        self.x = x
        self.y = y
        self.theta = theta
        self.pose = robotbasics.Pose(x,y,theta)
        self.localEyeList = list()
        self.weight = 1
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
        
class HypobotCloud:
    """
    This class is a wrapper for hypobotList.  It includes functions for
    weighting, generating
    """
    def __init__(self):
        self.hypobotList = list()
    def clear(self):
        l = len(self.hypobotList)
        self.hypobotList = list()
        print("deleted " + str(l) + " hypobots.  No hypobots left.")
    def appendGaussianCloud(self, cloudSize, pose, poseSigma):
        import random 
        for i in range (0,cloudSize):
            x = pose.x + random.gauss(pose.x, poseSigma.x)
            y = pose.y + random.gauss(pose.y, poseSigma.y)
            theta = pose.theta + random.gauss(pose.theta, poseSigma.theta)
            self.hypobotList.append(Hypobot(x,y,theta))
            print("Added hypobot at x,y,theta")
    def appendBlanket(self, cloudRootSize, theta):
        #blankets the field with cloudRootSize*CloudRootSize hypobots
        l = 7/(cloudRootSize - 1)
        for i in range(0,cloudRootSize):
            for j in range(0,cloudRootSize):
                self.hypobotList.append(Hypobot(.5 + l*i, .5+l*j, theta))
    def generateEyeData(self, landmarkList):
        for hypobot in self.hypobotList:
            hypobot.generateEyeData(landmarkList)
    def weight(self):
        for hypobot in self.hypobotList:
            hypobot.weight()
    def normalizeWeights(self):
        #this method scales the weights so the lowest is 0 and the highest is 1
        #go through the hypbobots
        minWeight = 1
        maxWeight = 0
        for hypobot in self.hypobotList:
            minWeight = min(minWeight, hypobot.weight)
            maxWeight = max(maxWeight, hypobot.weight)
        #adjust the weights to span from 0 to 1
        for i in range(len(self.hypobotList)):
            hypobot = self.hypobotList[i]
            hypobot.weight = (hypobot.weight - minWeight)/(maxWeight-minWeight)
    def collapse(self, threshold):
        #this method "collapses" the wavefunction, averaging over all weights above threshold
        #threshold of .5 seems to work well
        self.normalizeWeights()
        #do a weighted average:
        avg = Pose(0,0,0)
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
                hypobotList.remove(hypobot)
        print("Pruned "+str(deleted)+" hypobots. "+
                str(len(self.hypobotList))+" remain.")
