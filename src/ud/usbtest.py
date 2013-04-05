import csv
import subprocess

print("Write code that reads from the USB here")
script = "echo robot | sudo -S mount /dev/disk/by-label/IEEER5 /mnt/robo"
proc = subprocess.Popen(['bash', '-c', script], 
	stdout=subprocess.PIPE)
stdout = proc.communicate()
USB = open("/mnt/robo/Locatio.csv")
reader = csv.reader(USB)
puckSector = []
for row in reader:
	puckSector.append(row)
print puckSector
