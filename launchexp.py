import os
import sys
import shutil
import time

#starts the emulator from scratch
def startEmulator():
    os.popen("emulator -avd leakAVD -wipe-data")
    time.sleep(50)

#main testing loop
print("Starting FunesDroid Testing...")
startEmulator()
#lifecycle event sequences to trigger
#les=["doc","bf","stai"]
les=["doc"]
#length of lifecycle event sequences to trigger
#nevent=[1,2,10]
nevent=[1]
#nevent=[2]
# wait time
#wtime=[1,2,5];
wtime=[5];
os.popen("adb devices")

for t in wtime:
	for event in les:
		for number in nevent:
			print("Starting new experiment, event: "+event+", number of les: "+str(number))
			cmd = "python AndroLeak.py emulator-5554 "+event+" "+str(number)+" "+str(t)
			os.system(cmd)

#close the emulator
os.popen("adb -s emulator-5554 emu kill")
time.sleep(50)
print("Testing Accomplished!")

