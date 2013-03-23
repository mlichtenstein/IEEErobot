import random

f = open('sensors.txt', 'r+')
g = f.readlines()

logic = list(range(len(g)))
occurances = list(range(len(g)))

for line in range(len(g)):
    g[line]=g[line].rstrip('\n')
    logic[line] = g[line].split(",")[0]
    occurances[line] = int(g[line].split(",")[1])

print logic
print occurances

sumOfOccurances=0
for i in range(len(g)):
    sumOfOccurances+=occurances[i]

randy = random.randint(1,sumOfOccurances)
runningTotal=0
chosenIndex=0
for i in range(len(occurances)):
    if runningTotal <= randy:
        runningTotal+=occurances[i]
    if runningTotal >= randy:
        chosenIndex = i
        break

parentA = logic[chosenIndex]
parentB = parentA
while(parentA==parentB):
    randy = random.randint(1,sumOfOccurances)
    runningTotal=0
    chosenIndex=0
    for i in range(len(occurances)):
        if runningTotal <= randy:
            runningTotal+=occurances[i]
        if runningTotal >= randy:
            chosenIndex = i
            break
    parentB = logic[chosenIndex]

string = ""
randomLogic=random.randint(0,1)
if randomLogic == 1:
    string +="("
else:
    string +="not("
string += "(" + parentA + ")"

randomLogic=random.randint(0,1)

if randomLogic == 0:
    string +="or("
else:
    string +="and("
string += parentB + "))"

print string


f.close()