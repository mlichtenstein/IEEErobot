class Eye:
    def __init__(self, x_offset, y_offset, theta_offset,
                    dataPointNum, subtendedAngle):
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
        self.IR[dataPoint] = IR
        self.US[dataPoint] = US

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
        print id(self.localEyeList)
        self.weight = 1
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
                self.weight *= math.exp((-(distance)**2)*.008)
        self.color = (  int(hypobot.weight*self.red),
                        int(hypobot.weight*self.green),
                        int(hypobot.weight*self.blue))
    def generateEyeData(self, real_eyeList, landmarkList):
        #tricky, we need to use the hardware info from real_eyeList
        #plus the pose info from hypobot to transform our heading
        import copy
        self.localEyeList = copy.deepcopy(real_eyeList) #gets the x, y, theta data
        #important that it be a deep copy, since each hbot really should have its own version of the data
        for eye in real_eyeList:
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
        return len(self.hypobotList())
    def appendBloom(self, multiplier, poseSigma):
        import random
        for hypobot in self.hypobotList:
            for i in range(0,mulitplier):
                pose = hypobot.pose
                while 1:
                    x = pose.x + random.gauss(pose.x, poseSigma.x)
                    y = pose.y + random.gauss(pose.y, poseSigma.y)
                    if x>.5 and x<7.5 and y>.5 and y<7.5:
                        break
                theta = pose.theta + random.gauss(pose.theta, poseSigma.theta)
                self.hypobotList.append(Hypobot(x,y,theta))
    def appendGaussianCloud(self, cloudSize, pose, poseSigma):
        import random 
        for i in range (0,cloudSize):
            while 1:
                x = pose.x + random.gauss(pose.x, poseSigma.x)
                y = pose.y + random.gauss(pose.y, poseSigma.y)
                if x>.5 and x<7.5 and y>.5 and y<7.5:
                    break
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
            hypobot.changeWeight()
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

def messageTupleToEyeList(messageTuple):
    string = messageTuple[2]
    dataPointStringList = string.split('|')
    import world
    eyeList = world.World().eyeList
    for dataPointString in dataPointStringList:
        dataPoint = dataPointString.split(',')
        index = dataPoint[0]
        IRlsb = dataPoint[1]
        IRmsb = dataPoint[2]
        USlsb = dataPoint[3]
        USmsb = dataPoint[4]    
        eyeNum = dataPoint[5]
        IR = IRmsb*256 + IRlsb
        US = USmsb*256 + USlsb
        eyeList[eyeNum].takeReading(dataPoint,IR,US)
    return eyeList
    
