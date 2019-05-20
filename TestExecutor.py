# -*- coding: utf-8 -*-
from subprocess import call
from subprocess import Popen
import subprocess
import shutil 
import os, sys
import time
from datetime import datetime
import math
sys.path.insert(0, 'Utils')
from AndroLeakUtil import *

# SINTASSI DELLO SCRIPT
# python TestExecutor.py [target device] [apk file] [stimulus type] [stimulus number] [samples number].
# target device: target device on wich make experiments.
# apk file: input apk file.
# stimulus type: type of stimulus. It can be "doc" or 1, "bf" or 2 , "stai" or 3. 
# stimulus number: number of rotations (or any stimulus) to do.
# samples number: number of samples to do.

# EXAMPLE
# python TestExecutor.py layout.apk 1 4 2

#Definisco i tempi di attesa (in secondi)
WAIT_TIME=0.8
LONG_WAIT_TIME=1

# INIZIO CORPO DELLO SCRIPT

#Recupero i parametri di input dello script
li = sys.argv
script_path = li[0] #Salvo il path dello script perchè mi è utile successivamente. 
li.pop(0) #Cancello il parametro 0 perchè qui non mi serve. 
if (len(li)==5): 
    DEVICE = li[0] 
    apk_name = li[1]
    stimulus_type = li[2]
    rot_numbers = int(li[3])
    WAIT_TIME = int(li[4])
    sam_numbers = 1
else: #Se non sono stati specificati parametri setto quelli di default.
    print("WARNING. Working on default value parameters.")
    DEVICE="emulator-5554" #Di default il device è l'emulatore
    apk_name="app.apk"
    rot_numbers=1
    sam_numbers=1
    stimulus_type="doc"

#Effettuo una input validation. 
if(".apk" not in apk_name):
    raise ValueError('You have to specify the apk name!')

if(rot_numbers<=0):
     raise ValueError('The Number of rotations must be positive.')

if(sam_numbers<=0):
    raise ValueError('The Samples Size must be positive.')

if(rot_numbers>10000):
     raise ValueError('The Number of rotations must be lower than 10000.')

if(sam_numbers>10000):
    raise ValueError('The Samples Size must be lower than 10000.')

if(stimulus_type=="1"):
    stimulus_type="doc"
elif(stimulus_type=="2"):
    stimulus_type="bf"
elif(stimulus_type=="3"):
    stimulus_type="stai"

if((stimulus_type!="doc") and (stimulus_type!="bf") and (stimulus_type!="stai")):
    raise ValueError('The Stimulus Type parameter has not an allowed value.')

#Calcolo ogni quante rotazioni occorre effettuare un dump, in funzione del numero di campioni indicato. 
now_dump = math.ceil(rot_numbers/sam_numbers)

#Set global values
setGlobalValues(DEVICE,WAIT_TIME,LONG_WAIT_TIME)

#Crea l'Android Manifest a partire dall'apk.
print("Extracting AndroidManifest.xml")
call(['java','-jar','Utils/apktool.jar','f','d',apk_name])

#Copio il manifest nella directory corrente.
my_path = get_script_path(script_path)
ManifestRelativePath = apk_name.replace(".apk","")
ManifestRelativePath = ManifestRelativePath.replace("InputAPKs/","")
shutil.copy(ManifestRelativePath+'/AndroidManifest.xml', my_path+'/')

#Installa l'apk sul dispositivo
print("Installing apk " + apk_name)
call(['adb','-s',DEVICE,'install','-g','-l',apk_name])

#Disabilita accellerometro su dispositivo
os.system("adb -s "+DEVICE+" shell content insert --uri content://settings/system --bind name:s:accelerometer_rotation --bind value:i:0")

#Lista tutte le activity e salva il risultato in un file temporaneo,
#effettuando il parsing dell'AndroidManifest.xml.
print("Parsing AndroidManifest.xml")
results = os.system("java -jar Utils/ManifestParser.jar AndroidManifest.xml > tmpFile")

#Pongo adb in root state
os.system("adb -s "+DEVICE+" root")

# Recupera le attività ed il package dal file temporaneo
f = open("tmpFile")
tokens = f.read()
tokens = tokens.split()
package = tokens[1]
tokens.remove("PACKAGE")
tokens.remove("ACTIVITIES")
tokens.remove(package)
activities = tokens
f.close()

#Stampo informazioni utili
print("App Package: " + package)

#Torno in home e resetto (occorre iniziare gli esperimenti dalla Home).
print("App resetting")
os.system("adb -s "+DEVICE+" shell am force-stop "+package)
os.system("adb -s "+DEVICE+" shell input keyevent KEYCODE_HOME")

# ESPERIMENTI
print("Starting experiments")

#Registro data e ora inizio esperimenti
log = [] # Preparo il log (registro delle activity)
gc_log = [] # Preparo il log del GC
dump_log = [] # Preparo il log dei dump
cpu_usage_log = [] # Preparo il log relativo all'utilizzo della cpu
logcat_starttime = time.strftime("%m-%d "+"%H:%M:%S")+".00" # Utile per il comando logcat
StartingExperimentsTime = time.strftime("%d/%m/%Y "+"%I:%M:%S")
cmd = "adb -s "+DEVICE+" logcat"
logcat_popen = subprocess.Popen(cmd,stdout=open("logcat.txt", 'w'),shell=True) #Avvio il logcat
num_activities = len(activities)
num_crashed_activities = 0

try:
    count=0
    # Per ogni activity...
    for a in activities:
         #Gestisco variabili utili
         count = count+1 #conteggio
         dump_log = [] # resetto il log dei GC perchè diverso per ogni activity.

         #Controllo se l'activity deve essere testata
         #if(not is_on_white_list(a)):
         #    continue;

         #Estraggo il nome dell'activity da porre in esecuzione. 
         if(package not in a): # Se l'activity non mi contiene il nome del package la salto. 
             print("SKIPPING ERROR on " + a)
             print("[ERROR] Package: "+package+" "+" Activity: "+a)
             log_error(log,a,'true',"Skipping Error")
             num_crashed_activities=num_crashed_activities+1 #Conteggio delle Activity crashate
             continue
         a_name = a.split("/.")[1] #nome activity
         
         #Se non esiste la directory di risultato la creo
         destination_path = "Results/"+package+"/"+a_name+"/" #path del file risulato
         if not os.path.exists(destination_path):
              os.makedirs(destination_path)

         #Torno in home e resetto
         print("App resetting")
         os.system("adb -s "+DEVICE+" shell am force-stop "+package)
         
         #Lancio l'activity
         print("Launching activity "+a)
         os.system("adb -s "+DEVICE+" shell am start -n "+a)
         os.system("adb -s "+DEVICE+" shell content insert --uri content://settings/system --bind name:s:user_rotation --bind value:i:0")

         #Salvo un riferimento all'activity corrente
         cmd = "adb -s "+DEVICE+" shell \" dumpsys activity | grep top-activity\""
         launched_activity = os.popen(cmd).read()
         time.sleep(LONG_WAIT_TIME)

         #Controllo se l'activity è stata lanciata correttamente (Check 1)
         time.sleep(LONG_WAIT_TIME)
         if(error_check(launched_activity,package,a_name)=="true"):
             print("ERROR on " + a_name)
             log_error(log,a_name,'true',"Launch failed [Check 1]")
             shutil.rmtree(destination_path) # Cancello la cartella risultato dell'Activity crashata
             num_crashed_activities = num_crashed_activities+1 #Conteggio delle activity crashate
             continue # Se c'è stato un errore non stimolo l'activity.

         #Forzo una Garbage Collection
         garbage_collector(gc_log,package)
         time.sleep(WAIT_TIME)

         #Forzo una Garbage Collection
         garbage_collector(gc_log,package)
         time.sleep(WAIT_TIME)

         #Effettuo un Dump della memoria heap dell'app
         print("Dumping heap (Before)")
         cmd = "adb -s "+DEVICE+" shell am dumpheap "+package+" /data/local/tmp/"+package+"_before_"+a_name+".hprof"
         result = os.popen(cmd).read()
         time.sleep(WAIT_TIME)
         cmd = "adb -s "+DEVICE+" pull /data/local/tmp/"+package+"_before_"+a_name+".hprof " + destination_path
         result = os.popen(cmd).read()
         dump_log.append("----- "+a_name+" -----\n")
         dump_log.append(datetime.now().strftime("%H:%M:%S.%f")+" Dump Heap (Before).\n")
         time.sleep(WAIT_TIME)
         hprof_file = convert_hprof(destination_path+package+"_before_"+a_name)
         make_histogram(hprof_file,package,a_name,-1)
         
         #Effettuo gli stimoli (rotazioni, background-foreground o STAI) ed i dump ogni tot. stimoli
         dump_count = 0
         for i in range(0,rot_numbers):
             dump_count = dump_count + 1 # Incremento variabile di conteggio
             do_stimulus(stimulus_type) # Effettuo lo stimolo
             # Se lo stimolo ha causato un errore torno in home
             if(error_check(launched_activity,package,a_name)=="true"):
                 print("Error. The current activity is not the launched one. Returning in home.")
                 os.system("adb -s "+DEVICE+" shell input keyevent KEYCODE_HOME")
                 break
            # Se ho raggiunto il numero now_dump effettuo un dump della memoria, e genero i CSV con andromat. 
             elif(dump_count==now_dump):
                 dump_count=0
                 hprof_file = make_dump(package,a_name,i,destination_path,dump_log)
                 if(error_check(launched_activity,package,a_name)=="false"): # Se non ci sono errori effettuo l'istogramma. 
                     make_histogram(hprof_file,package,a_name,i) 

         #Controllo se l'activity attuale corrisponde a quella lanciata (Check 2)
         if(error_check(launched_activity,package,a_name)=="true"):
             print("ERROR on " + a_name)
             log_error(log,a_name,'true',"Activity has crashed after "+str(i+1)+" stimulus [Check 2]")
             num_crashed_activities=num_crashed_activities+1 # Conteggio delle Activity crashate
             #shutil.rmtree(destination_path) # Cancello la cartella risultato dell'Activity crashata
             continue    

         #Effettuo un dump post garbage-collector finale
         garbage_collector(gc_log,package)
         print("Dumping heap (After Garbage Collection)")
         cmd = "adb -s "+DEVICE+" shell am dumpheap "+package+" /data/local/tmp/"+package+"_afterGC_"+a_name+".hprof"
         result = os.popen(cmd).read()
         time.sleep(WAIT_TIME)
         cmd = "adb -s "+DEVICE+" pull /data/local/tmp/"+package+"_afterGC_"+a_name+".hprof " + destination_path
         result = os.popen(cmd).read()
         dump_log.append(datetime.now().strftime("%H:%M:%S.%f")+" Dump Heap (After GC).\n")
         time.sleep(WAIT_TIME)
         convert_hprof(destination_path+"/"+package+"_afterGC_"+a_name)

         #Cancello i file hprof dalla memoria del dispositivo
         cmd = "adb -s "+DEVICE+" shell rm -r /data/local/tmp/"+package+"_before_"+a_name+".hprof"
         os.system(cmd)

         #Calcolo l'istogramma differenza dei dump con HprofAnalyzer.jar
         print("Making Difference through HprofAnalyzer.jar")
         make_difference(destination_path,package,a_name,i)

         #Salvo nella cartella risultato dell'activity un log dei Dump effettuati. 
         save_dump_log(destination_path, dump_log)

         #Controllo se l'activity è crashata, ossia se corrisponde a quella lanciata (Check 3)
         if(error_check(launched_activity,package,a_name)=="true"):
             # Se ci sono stati errori: 
             print("ERROR on " + a_name)
             log_error(log,a_name,'true',"Activity crashed [Check 3]")
             shutil.rmtree(destination_path) # Cancello la cartella risultato dell'Activity crashata
             num_crashed_activities=num_crashed_activities+1 # Conteggio delle Activity crashate
             continue
         else:
             # Se non ci sono stati errori:
             log_error(log,a_name,'false',"") # Registro che non ci sono stati errori. 
             os.system("adb -s "+DEVICE+" shell am force-stop "+package) # Chiudo l'applicazione per pulire la memoria.

         #Printing Progress
         print("Progress on "+apk_name+": "+str(count)+" activities of "+str(num_activities)+" completed. ")
except:
    print("Unexpected error:"+str(sys.exc_info()[0]))
    raise
#Registro data e ora fine esperimenti
EndingExperimentsTime = time.strftime("%d/%m/%Y "+"%I:%M:%S")
logcat_popen.terminate() # Chiudo il logcat

#Torno in home e resetto
print("App resetting")
os.system("adb -s "+DEVICE+" shell am force-stop "+package)
os.system("adb -s "+DEVICE+" shell pm clear "+package)

#Controllo se la directory esiste. 
if not os.path.exists("Results/"+package+"/"):
          os.makedirs("Results/"+package+"/")

#Recupero logcat, ed i log relativi al GC da logcat
#cmd = "adb -s "+DEVICE+" logcat -d -t \""+logcat_starttime+"\"" # Comando per richiedere i log dal momento di inizio esperimento.
#os.system(cmd+" > logcat.txt") # Esecuzione del comando, salvo ouput in file temporaneo.
gc_log_2 = []
get_gc_logs("logcat.txt",gc_log_2) # Recupero i log di interesse (relativi al GC).

#Cancello il contenuto della cartella temporanea del device
print("Deleting tempopary files on "+DEVICE)
cmd = "adb -s "+DEVICE+" shell \"rm -f -r data/local/tmp/* \""
result = os.popen(cmd).read()

#Recupero i log di trace.txt
#os.system("adb -s "+DEVICE+" pull /data/anr/traces.txt Results/"+package+"/")
#os.system("adb -s "+DEVICE+" shell rm -r /data/anr/traces.txt")
#os.system("adb -s "+DEVICE+" shell /data/anr/traces.txt")

#Salvo una copia dell'AndroidManifest.xml e di logcat.txt
shutil.copy("AndroidManifest.xml", "Results/"+package+"/")
shutil.copy("logcat.txt","Results/"+package+"/")

#Creo il file config.txt
try:
    file = open("Results/"+package+"/"+package+"_config.txt","w")
    file.write("--- CONFIG ---\n")
    file.write("APK NAME: " + apk_name + "\n")
    file.write("PACKAGE: "+ package + "\n")
    file.write("STIMULUS TYPE: "+stimulus_type+"\n")
    file.write("STIMULUS NUMBER: " +str(rot_numbers)+ "\n")
    file.write("SAMPLE NUMBER: "+str(sam_numbers)+"\n")
    file.write("ONE SAMPLE EACH "+str(now_dump)+" STIMULUS\n")
    file.close()
except:
    print("Unexpected error:"+sys.exc_info()[0])
    raise

#Creo il file results.txt
try:
    file = open("Results/"+package+"/"+package+"_results.txt","w")
    file.write("--- RESULTS ---\n")
    file.write("START TIME: " + StartingExperimentsTime + "\n")
    file.write("END TIME: " + EndingExperimentsTime + "\n")
    file.write("NUMBER OF ACTIVITIES: "+str(num_activities)+"\n")
    file.write("NUMBER OF CRASHED ACTIVITIES: "+str(num_crashed_activities)+"\n")
    for line in log:
        file.write(line)
    file.write("--- GARBAGE COLLECTOR LOGS ---\n")
    for line in gc_log:
        file.write(line)
    file.close()
except:
    print("Unexpected error:"+str(sys.exc_info()[0]))
    raise

#Creo il file GClogs_from_logcat.txt
try:
    file = open("Results/"+package+"/GClogs_from_logcat.txt","w")
    for line in gc_log_2:
        file.write(line)
    file.close()
except:
    print("Unexpected error:"+sys.exc_info()[0])
    raise

#Creating LeakingReport.txt
makeLeakingReport(package)

#Riavvio di ADB
print("Restarting ADB service")
os.system("adb kill-server")
os.system("adb start-server")

#Cancello i file temporanei creati dallo script.
try:
    shutil.rmtree(ManifestRelativePath)
    os.remove("tmpFile")
    os.remove("AndroidManifest.xml")
    os.remove("logcat.txt")  
except:
    print("[ERROR DELETING TEMPORARY FILES] Error."+str(sys.exc_info()[0]))

os.rename("Results/"+package,"Results/"+package+"_"+stimulus_type+"_N"+str(rot_numbers)+"_t"+str(WAIT_TIME)+"_"+str(int(time.time())))	
print("Execution completed. You can find results in Results/ folder")
# Raffaele Sellitto. 02/01/2018. 


