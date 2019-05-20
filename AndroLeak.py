# -*- coding: utf-8 -*-
import os
import sys
import shutil
from subprocess import call
import time
sys.path.insert(0, 'Utils')
import AndroLeakUtil

# SINTASSI DEL COMANDO
# python AndroLeak.py [target device] [stimulus type] [stimulus number].
# target device: the device where to execute experiments on.
# stimulus type: type of stimulus (event lifecycle). It can be "doc" or 1, "bf" or 2 , "stai" or 3. 
# stimulus number: number of event lifecycles to do.

# Warning. "InputAPKs\" folder must contain all the apk files to execute.

# EXAMPLE
# python AndroLeak.py emulator-5554 doc 4

help = 'python AndroLeak.py [target device] [stimulus type] [stimulus number].\n'
help += 'target device: the device where to execute experiments on.\n'
help += 'stimulus type: type of stimulus (event lifecycle). It can be \'doc\' or 1, \'bf\' or 2 , \'stai\' or 3.'
help += '\nstimulus number: number of event lifecycles to do.\n'
help += 'Warning. \'InputAPKs\\\' folder must contain all the apk files to execute.\n'
help += 'EXAMPLE: python AndroLeak.py emulator-5554 doc 4'

WAIT_TIME=1
LONG_WAIT_TIME=2
DEVICE="emulator-5554"

#Function that reboot the emulator.
def rebootEmulator():
    #os.system("adb -s "+DEVICE+" -e reboot")
    os.system("emulator -avd "+DEVICE+" -wipe-data")
    time.sleep(5)
    waitDeviceHasBooted()

#Function that wait that the Emulator has booted.
def waitDeviceHasBooted():
    maxiter=1000; count=0;
    result=os.popen("adb -s "+DEVICE+" shell getprop sys.boot_completed").read()
    while("1" not in result):
        print("adb -s "+DEVICE+" shell getprop sys.boot_completed")
        result=os.popen("adb -s "+DEVICE+" shell getprop sys.boot_completed").read()
        print("Waiting the Emulator")
        time.sleep(2)
        count+=1;
        if(count==maxiter): #If maxites is reached probably the emulator is crashed.
            print("ERROR: The emulator is offline.")
            raise SystemExit(0);

#Se la directory è vuota lancio un errore.
if os.listdir("InputAPKs") == []: 
    raise ValueError('InputAPKs\ is empty. You must put some apk files in InputAPKs\.')

#Aspetto, eventualmente, che il device finisca il boot
waitDeviceHasBooted()

#Recupero il numero di rotazioni e campionamenti dall'input
li = sys.argv
if(len(li)==2):
    if(li[1]=='-h' or li[1]=='--help' or li[1]=='h' or li[1]=='help'):
        print(help);
        raise SystemExit(0);
    else:
        raise SyntaxError('You are using this command wrongly. Check the syntax (use the option help). ')
elif(len(li)==5):
    DEVICE = li[1]
    stimulus_type = li[2]
    num_rotations = int(li[3])	
    WAIT_TIME = int(li[4])
    sample_size = 1
    REBOOT_TIME = 0
else:
    raise SyntaxError(str(len(li))+' You are using this command wrongly. Check the syntax (use the option help). ')

# Input Validation.
if(sample_size>10000 or sample_size <=0):
    raise SyntaxError('You are using this command wrongly. The Sample Size must be >0 and <10000. ') 
if(num_rotations>10000 or num_rotations <=0):
    raise SyntaxError('You are using this command wrongly. The Stimulus Numbers must be >0 and <10000. ') 
if(sample_size>num_rotations):
    raise SyntaxError('You are using this command wrongly. The Sample Size must be bigger than Stimulus Numbers. ') 

# Avviso, su Windows, che il FileSystem non deve avere limiti sulla lunghezza dei nomi delle directory.
if os.name == 'nt':
    print("---------------------------------------------------------")
    print("WARNING. Be sure that NTFS has LongPathsEnabled.")
    print("---------------------------------------------------------")

# Se la cartella InputAPKs/ è vuota lancio un errore. 
if os.listdir("InputAPKs/")=="":
    raise SyntaxError("InputAPKs/ folder is empty!")

#Se non esiste la directory InputAPK la creo.
if not os.path.exists("InputAPKs/"):
    os.makedirs("InputAPKs")

#Se non esiste la directory Results la creo.
if not os.path.exists("Results/"):
    os.makedirs("Results/")

print("---------------------------------------------------------")
print("WARNING. The experiments are going to be executed on "+DEVICE+".")
print("---------------------------------------------------------")

#Installa l'apk STAI sul dispositivo (utile per sollecitare l'evento STAI)
if(stimulus_type=="stai" or stimulus_type=="3"):
    call(['adb','-s',DEVICE,'install','-g','-l','Utils/stai.apk'])

# Setting device's date and time MMDDhhmm[[CC]YY][.ss]
device_time = time.strftime("%d/%m/%Y "+"%I:%M:%S")
device_time_dformat = time.strftime("%m%d%H%M%Y.%S")
print("Setting Device's date and time to: "+device_time)
cmd = "adb -s "+DEVICE+" shell \"su 0 toybox date "+device_time_dformat+"\""
os.system(cmd)

#Listo gli apk contenuti nella cartella InputAPKs/
apks_list = os.listdir("InputAPKs/")

#Effettuo gli esperimenti per ogni apk
StartingExperimentsTime = time.strftime("%d/%m/%Y "+"%I:%M:%S")
print("Starting experiments: " + StartingExperimentsTime)
i = 0
count = 0
num_apk = len(apks_list)

for a in apks_list:
    if(REBOOT_TIME>0 and count==REBOOT_TIME):
        count=0
        rebootEmulator()
    print("----- Starting experiments on application " + a + " -----")
    time.sleep(WAIT_TIME)
    apk_to_execute = "InputAPKs/"+a
    print(apk_to_execute)
    cmd = "python TestExecutor.py "+DEVICE+" "+apk_to_execute+" "+stimulus_type+" "+str(num_rotations)+" "+str(WAIT_TIME)+" "
    os.system(cmd)
    i=i+1
    count=count+1
    AndroLeakUtil.printProgressBar(i,num_apk,length=30) # Displaying Progress Bar
    waitDeviceHasBooted() # Useful in cases of Emulator crashes
        
EndingExperimentsTime = time.strftime("%d/%m/%Y "+"%I:%M:%S")
print("Ending experiments: " + EndingExperimentsTime)

#Riabilita accellerometro su dispositivo
os.system("adb -s "+DEVICE+" shell content insert --uri content://settings/system --bind name:s:accelerometer_rotation --bind value:i:1")

#Genera il Report finale
AndroLeakUtil.makeAndroLeakReport()

#Creo il file results.txt
#Se non esiste la directory di risultato la creo
if not os.path.exists("Results/"):
    os.makedirs("Results")
file = open("Results/AndroLeak_results.txt","w") 
file.write("--- RESULTS ---\n")
file.write("You can find results of each experiment into the various folders.\n")
file.write("START TIME: " + StartingExperimentsTime + "\n")
file.write("END TIME: " + EndingExperimentsTime + "\n")
file.close()
# Raffaele Sellitto. 09/12/2017. 
