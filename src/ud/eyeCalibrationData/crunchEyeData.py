f = open("calibData1364867374.62", 'r')
dp = f.readlines()
for line in dp:
	for i in range(0,5):
		j = line.split(",")[i]
		line[i]=int(j)
i=0
while i < len(dp):
	if dp[i][0]==dp[i+1][0]:
		avg = 0
		if dp[i][0] == dp[i+2][0]:
			for j in [0,1]:
				avg += dp[i][j]+dp[i+1][j]+dp[i+2][j]
			avg /= 6
			print (i,avg)
			i = i + 3
		else:
			for j in [0,1]:
				avg += dp[i][j]+dp[i+1][j]
			avg /= 4
			print (i, avg)
			i = i +2
