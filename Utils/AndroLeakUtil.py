# -*- coding: utf-8 -*-
import os
import csv
import sys
import time
import shutil
from datetime import datetime

# FUNZIONI UTILIZZATE IN ANDROLEAK

# Function that sets different values of the global variables. 
def setGlobalValues(device,wait_time,long_wait_time):
    global WAIT_TIME;
    global LONG_WAIT_TIME;
    global DEVICE;
    WAIT_TIME=wait_time;
    LONG_WAIT_TIME=long_wait_time;
    DEVICE=device;

# Funzione che riporta la directory dello script
def get_script_path(script_path):
    return os.path.dirname(os.path.realpath(script_path))

# Funzione che logga il risultato dell'esecuzione dell'activity
def log_error(log,a_name,had_errors,crash_note):
    timestamp = time.strftime("%d/%m/%Y "+"%I:%M:%S")
    if(had_errors=='true'):
        log.append("["+timestamp+"] "+ a_name + " NOT OK. ERROR: "+crash_note+"\n")
    else:
        log.append("["+timestamp+"] "+ a_name + " OK. \n")

#Funzione che effettua un dump della memoria heap dell'applicazione
def make_dump(package,a_name,count,destination_path,dump_log):
    print("Dumping heap (After "+str(count+1)+")")
    hprof_file_name = package+"_"+str(count+1)+"_after_"+a_name
    cmd = "adb -s "+DEVICE+" shell am dumpheap "+package+" /data/local/tmp/"+hprof_file_name+".hprof"
    result = os.popen(cmd).read()
    dump_log.append(datetime.now().strftime("%H:%M:%S.%f")+" Dump Heap (After "+str(count+1)+").\n")
    time.sleep(WAIT_TIME)
    cmd = "adb -s "+DEVICE+" pull /data/local/tmp/"+hprof_file_name+".hprof "+ destination_path
    result = os.popen(cmd).read()
    time.sleep(WAIT_TIME)
    cmd = "adb -s "+DEVICE+" shell rm -r /data/local/tmp/"+hprof_file_name+".hprof"
    os.system(cmd)
    time.sleep(WAIT_TIME)
    convert_hprof(destination_path+"/"+hprof_file_name)
    return destination_path+hprof_file_name+"_conv.hprof"

#Funzione che salva su file il contenuto del log dei Dump.
def save_dump_log(destination_path, dump_log):
    file = open(destination_path+"/DumpLog.txt","w")
    for line in dump_log:
        file.write(line)
    file.close()

#Funzione per convertire gli hprof nel formato Eclipse MAT
def convert_hprof(hprof_to_convert):
    if(os.name=='nt' or os.name=='posix'): # Controllo se sono su Windows o Linux perchè su altri OS il comando cambia.
        cmd = "hprof-conv "+hprof_to_convert+".hprof "+hprof_to_convert+"_conv.hprof"
        os.system(cmd)
        #print("[DEBUG] Ececuting command: "+cmd)
    else:
        raise ValueError("convert_hprof function is not available for your os.")
    return hprof_to_convert+"_conv.hprof"

#Funzione che effettua un Garbage Collector
def garbage_collector(gc_log,package):
    print("Garbage Collection")
    os.system("adb -s "+DEVICE+" root")
    timestamp=datetime.now().strftime("%H:%M:%S.%f")
    pid = os.popen("adb -s "+DEVICE+" shell pidof "+package).read()
    os.system("adb -s "+DEVICE+" shell kill -10 " + pid)
    time.sleep(WAIT_TIME)
    gc_log.append("["+timestamp+"] Garbage Collection required.\n")

#Funzione che estrae dal file logcat i log relativi all'attivazione del GC
def get_gc_logs(logcat_file,gc_log):
    line_marker = "GC freed"
    try:
        file = open(logcat_file)
        for line in file:
            if line_marker in line:
                gc_log.append(line)
        file.close()
    except:
        print("[ERROR GC LOG] Unexpected error:"+str(sys.exc_info()[0]))

#Funzione che effettua la differenza degli hprof attraverso HprofAnalyzer.jar
def make_difference(destination_path,package,a_name,i):
     hprof_b = destination_path+package+"_before_"+a_name+"_conv.hprof"
     hprof_a = destination_path+package+"_"+str(i+1)+"_after_"+a_name+"_conv.hprof"
     hprof_agc = destination_path+package+"_afterGC_"+a_name+"_conv.hprof"
     #Checking if the necessary files exist and have size > 0. If not i close the application.
     cond1 = os.path.isfile(hprof_a) and os.path.getsize(hprof_a) > 0
     cond2 = os.path.isfile(hprof_agc) and os.path.getsize(hprof_agc) > 0
     cond3 = os.path.isfile(hprof_b) and os.path.getsize(hprof_b) > 0
     try:
         if(cond1 and cond2 and cond3):
             cmd = "java -jar Utils/HprofAnalyzer.jar "+package+" "+hprof_a+" "+hprof_b #Differnza after-before
             os.system(cmd)
             cmd = "java -jar Utils/HprofAnalyzer.jar "+package+" "+hprof_agc+" "+hprof_b #Differenza afterGC-before
             os.system(cmd)
             csv_file1="Difference_snapshot_Results_"+package+"_"+a_name+"_"+package+"_"+str(i+1)+"_after_"+a_name+"_conv.csv"
             csv_file2="Difference_snapshot_Results_"+package+"_"+a_name+"_"+package+"_afterGC_"+a_name+"_conv.csv"
             shutil.copyfile(csv_file1, destination_path+"Difference_After.csv")
             shutil.copyfile(csv_file2, destination_path+"Difference_AfterGC.csv")
             #os.remove(csv_file1);
             #os.remove(csv_file2);
         else:
             print("Activity closing due Error")
             os.system("adb -s "+DEVICE+" shell input keyevent KEYCODE_HOME")
     except:
         print("[ERROR MAKING DIFFERENCE] Unexpected error:"+str(sys.exc_info()[0]))

#Funzione che effettua l'istogramma attraverso HprofAnalyzer.jar
def make_histogram(hprof_file,package,a_name,i):
    #Calcolo l'istogramma del dump appena effettuato con HprofAnalyzer.jar, se un file hprof è stato creato.
    try:
        if (os.path.isfile(hprof_file) and os.path.getsize(hprof_file) > 0): #Checking if the necessary files exist. If not i close the application.
            print("Making Histogram through HprofAnalyzer.jar")
            cmd = "java -jar Utils/HprofAnalyzer.jar "+package+" "+hprof_file
            print("-------------")
            print(cmd)
            print("-------------")
            #os.system("pause")
            os.system(cmd)
            destination_path="Results/"+package+"/"+a_name+"/";
            if(i>=0): 
                csv_file="Histogram_snapshot_Results_"+package+"_"+a_name+"_"+package+"_"+str(i+1)+"_after_"+a_name+"_conv.csv"
                shutil.copyfile(csv_file,destination_path+package+"_"+str(i+1)+"_after_"+a_name+"_conv.csv")
            elif(i==-1): # Se sono al primo dump il file avrà nome diverso. 
                csv_file="Histogram_snapshot_Results_"+package+"_"+a_name+"_"+package+"_before_"+a_name+"_conv.csv"
                shutil.copyfile(csv_file,destination_path+package+"_0_before_"+a_name+"_conv.csv")
            elif(i==99): # Se sono al primo dump il file avrà nome diverso. 				
                csv_file="Histogram_snapshot_Results_"+package+"_"+a_name+"_"+package+"_afterGC_"+a_name+"_conv.csv"
                shutil.copyfile(csv_file,destination_path+package+"_afterGC_"+a_name+"_conv.csv")				
            else:
                raise ValueError("You are using make_histogram() in a wrong way.")
            os.remove(csv_file)
        else:
            print("Activity closing due Error")
            os.system("adb -s "+DEVICE+" shell input keyevent KEYCODE_HOME")
    except:
        print("[ERROR MAKING HISTOGRAMS] Unexpected error:"+str(sys.exc_info()[0]))

#Funzione che controlla se l'activity attuale corrisponde a quella lanciata, e se il package corrisponde a quello dell'applicazione.
def error_check(launched_activity,package,a_name):
     cmd = "adb -s "+DEVICE+" shell \"dumpsys activity | grep top-activity\""
     current_package = os.popen("adb -s "+DEVICE+" shell \"dumpsys window windows | grep mCurrentFocus | cut -d'/' -f1\"").read();
     current_activity_name = os.popen("adb -s "+DEVICE+" shell \"dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp'\"").read();
     time.sleep(WAIT_TIME)
     if((package not in current_package) or (a_name not in current_activity_name)):
         return "true"
     else:
         return "false"

#Funcione che effettua tramite ADB gli stimoli (rotazioni, background-foreground, STAI), adottando wait per assestare transitori. 
def do_stimulus(STIMULUS):
    if(STIMULUS=='bf'):
        print("Background Foreground")
        os.system("adb -s "+DEVICE+" shell input keyevent KEYCODE_HOME")
        time.sleep(WAIT_TIME)
        os.system("adb -s "+DEVICE+" shell input keyevent KEYCODE_APP_SWITCH")
        time.sleep(WAIT_TIME)
        os.system("adb -s "+DEVICE+" shell input keyevent KEYCODE_APP_SWITCH")
        time.sleep(WAIT_TIME)
    elif(STIMULUS=='doc'):
        print("Rotating")
        os.system("adb -s "+DEVICE+" shell content insert --uri content://settings/system --bind name:s:user_rotation --bind value:i:1")
        time.sleep(WAIT_TIME)
        os.system("adb -s "+DEVICE+" shell content insert --uri content://settings/system --bind name:s:user_rotation --bind value:i:0")
        time.sleep(WAIT_TIME)
    elif(STIMULUS=='stai'):
        print("Stai")
        os.system("adb -s "+DEVICE+" shell am start -n com.klinker.android.floating_window/.PopupMainActivity")
        time.sleep(WAIT_TIME)
        os.system("adb -s "+DEVICE+" shell input keyevent KEYCODE_BACK")
        time.sleep(LONG_WAIT_TIME)
    else:
        raise ValueError('You are using do_stimulus() in a wrong way')

#Controlla se l'activity deve essere testata.
def is_on_white_list(activity):
    result=False;
    f = open("activity-white-list.txt")
    tokens = f.read();
    tokens = tokens.split()
    for token in tokens:
        if(activity in token):
            result=True;
    f.close();
    return result

# Function that print the iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '_' * (length - filledLength)
    print('PROGRESS STATE: '+prefix+' |'+bar+'| '+percent+'% '+suffix+'\n')

# Realize through HprofAnalyzer.jar
def makeAfterGC_CSV():
    directories = os.listdir("Results/"); # Per ogni directory in Results/
    for package in directories:
        if(os.path.isdir("Results/"+str(package)+"/")): # Se la directory è una folder...
            package_directories = os.listdir("Results/"+str(package)+"/") # Per ogni directory nella cartella package
            for activity in package_directories:
                if(os.path.isdir("Results/"+str(package)+"/"+activity+"/")): #Se c'è una cartella risultato dell'activity.
                    hprof_file = "Results/"+str(package)+"/"+activity+"/"+str(package)+"_afterGC_"+str(activity)+"_conv.hprof"
                    if(os.path.isfile(hprof_file)):
                        cmd = "java -jar Utils/HprofAnalyzer.jar "+package+" "+hprof_file
                        os.system(cmd)
                        destination_path="Results/"+str(package)+"/"+activity+"/"
                        csv_file = "Histogram_snapshot_Results_"+str(package)+"_"+str(activity)+"_"+str(package)+"_afterGC_"+str(activity)+"_conv.csv"
                        shutil.move(csv_file, destination_path+str(package)+"_AfterGC_"+str(activity)+"_conv.csv")

# Realize a Total Heap report reading the previous Results. 
def makeTotalHeapCSV():
    directories = os.listdir("Results/"); # Per ogni directory in Results/
    for package in directories:
        if(os.path.isdir("Results/"+str(package)+"/")): # Se la directory è una folder...
            package_directories = os.listdir("Results/"+str(package)+"/") # Per ogni directory nella cartella package
            Log = []
            Log.append("Activity,Total Heap (Before),Total Heap (After GC),Difference (After - Before)\n")
            for activity in package_directories:
                if(os.path.isdir("Results/"+str(package)+"/"+activity+"/")): #Se c'è una cartella risultato dell'activity.
                    csv_file = "Results/"+str(package)+"/"+activity+"/"+str(package)+"_afterGC_"+str(activity)+"_conv.csv"
                    if(os.path.isfile(csv_file)):
                        open_file=open(csv_file,'r')
                        file_lines=open_file.readlines()
                        first_line = file_lines[0].strip()  # First Line
                        total_heap_AfterGC = int(first_line.split(' ')[-1])
                        csv_file = "Results/"+str(package)+"/"+activity+"/"+str(package)+"_0_before_"+str(activity)+"_conv.csv"
                        open_file=open(csv_file,'r')
                        file_lines=open_file.readlines()
                        first_line = file_lines[0].strip()  # First Line
                        total_heap_0 = int(first_line.split(' ')[-1])
                        total_heap_difference = total_heap_AfterGC - total_heap_0
                        Log.append(str(activity)+","+str(total_heap_0)+","+str(total_heap_AfterGC)+","+str(total_heap_difference)+"\n")
            try:
                with open("Results/"+str(package)+"/TotalHeap.csv", "w") as csvfile: # Open the CSV file
                    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
                    for line in Log:
                        csvfile.write(line)
                    csvfile.close()
            except:
                print("Unexpected error writing TotalHeap.csv")
                raise

#Realize a TotalHeapFinalReport analyzing the TotalHeap result files.
def makeTotalHeapFinalReport():
    directories = os.listdir("Results/"); # Per ogni directory in Results/
    Log = []
    Log.append("Package,Total Heap Total Difference,Total Heap Positive Difference\n")
    for package in directories:
        if(os.path.isdir("Results/"+str(package)+"/")): # Se la directory è una folder...
            package_directories = os.listdir("Results/"+str(package)+"/") # Per ogni directory nella cartella package

            try:
                with open("Results/"+str(package)+"/TotalHeap.csv", "r") as csvfile: # Open the CSV file
                    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
                    next(spamreader)
                    th_total_difference=0
                    th_positive_difference=0
                    for row in spamreader:
                        difference=int(row[-1])
                        th_total_difference=th_total_difference+difference
                        if(difference>0):
                            th_positive_difference=th_positive_difference+difference
                    Log.append(str(package)+","+str(th_total_difference)+","+str(th_positive_difference)+"\n")
            except:
                print("Unexpected error reading TotalHeap.csv")
                raise
    try:
        with open("Results/TotalHeapFinalReport.csv", "w") as csvfile: # Open the CSV file
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for line in Log:
                csvfile.write(line)
            csvfile.close()
    except:
        print("Unexpected error writing TotalHeapFinalReport.csv")
        raise
        
   

# Function used by AndroLeak.py to create its final Report
def makeAndroLeakReport():
    listfiles = os.listdir("Results/")
    Log = []
    header="APK,Activities,Tested Activities,Leaked Activities,Total Shallow Heap,Total Retained Size\n"
    Log.append(header)

    # Recovering Difference_AfterGC.csv for each Results/package/activity
    for f in listfiles:
        package = str(f)
        if(os.path.isdir("Results/"+f)):
            ReportFile = "Results/"+f+"/LeakingReport.csv"
            ResultFile = "Results/"+f+"/"+package+"_results.txt"
            result1=""
            result2=""
            if(os.path.isfile(ResultFile)):
                f = open(ResultFile,"r")
                for line in f:
                    if("NUMBER OF ACTIVITIES:" in line):
                        tmp = str(line).split()
                        num_activities = tmp[-1]
                    elif("NUMBER OF CRASHED ACTIVITIES:" in line):
                        tmp = str(line).split()
                        num_crashed_activities = tmp[-1]
                tested_activities=str(int(num_activities)-int(num_crashed_activities));     
                result1 = package+","+num_activities+","+tested_activities
                f.close()
            if(os.path.isfile(ReportFile)):
                open_file=open(ReportFile,'r')
                file_lines=open_file.readlines()
                second_line = file_lines[1].strip()  # Second Line
                if("The application has no leaks!" not in second_line):
                    result2=","+str(second_line)+"\n"
                else:
                    result2=",0,0,0\n"
            Log.append(result1+result2)
                
    # Writing AndroleakReport.csv
    try:
        with open("Results/AndroLeakReport.csv", "w") as csvfile: # Open the CSV file
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for line in Log:
                csvfile.write(line)
            csvfile.close()
    except:
        print("Unexpected error writing LeakingReport.csv")
        raise

# Controlla se nel dump before ci sono 0 istanze di quella classe. Utile per evitare falsi positivi. 
def hasZeroIstancesInBeforeDump(class_to_check,CSV_BeforeDump):
    result=False;
    with open(CSV_BeforeDump) as csvfile: # Open the CSV file
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(spamreader, None)  # skip the headers
        for row in spamreader: # For each row
            class_name = row[0]
            num_objs=int(row[1]) #Getting instance number
            if(class_name==class_to_check):
                if(num_objs==0):
                    result=True;
        return result;


# Function used by ScriptADB.py to create its final report
def makeLeakingReport(package):
    # Useful variables
    APKhasLeaked = "False"
    listfiles = os.listdir("Results/"+package)
    LeakedLog = []
    ActivityLeakedLog = []
    numLeakedActivity = 0
    ShallowHeapTotal = 0
    RetainedSizeTotal = 0
    numActivityNoLeaked = 0

    # Recovering Difference_AfterGC.csv for each Results/package/activity
    for f in listfiles:
        if(os.path.isdir("Results/"+package+"/"+f)):
            CSVfile = "Results/"+package+"/"+f+"/Difference_AfterGC.csv"
            CSVfile_before = "Results/"+package+"/"+f+"/"+package+"_0_before_"+f+"_conv.csv"
            if(os.path.isfile(CSVfile) and os.path.isfile(CSVfile_before)):
                with open(CSVfile) as csvfile: # Open the CSV file
                    ActivityhasLeaked="False"
                    ActivityShallowHeap=0
                    ActivityTotalHeap=0
                    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
                    for row in spamreader: # For each row
                        class_name = row[0]
                        num_objs=int(row[1]) #Getting instance number
                        shallow_heap = int(row[2])
                        retained_size = int(row[3])
                        if(num_objs>0 and not hasZeroIstancesInBeforeDump(class_name,CSVfile_before)): # if num_obj is >0 there is a Memory Leak
                            ActivityShallowHeap = ActivityShallowHeap + shallow_heap
                            ActivityTotalHeap = ActivityTotalHeap + retained_size
                            if(ActivityhasLeaked=="False"): # If is the first Memory Leak...
                                LeakedLog.append("--- "+f+" has leaked ---") # logging this information
                                LeakedLog.append("Class Name,Istance Number,Shallow Heap,Retained Size")
                                numLeakedActivity = numLeakedActivity +1
                                ActivityhasLeaked="True"
                                APKhasLeaked="True"
                            LeakedLog.append(class_name+","+str(num_objs)+","+str(shallow_heap)+","+str(retained_size)) # appending the leaked row
                            ShallowHeapTotal = ShallowHeapTotal + shallow_heap
                            RetainedSizeTotal = RetainedSizeTotal + retained_size
                    if(ActivityhasLeaked=="True"):
                        ActivityLeakedLog.append(f+","+str(ActivityShallowHeap)+","+str(ActivityTotalHeap))
                    elif(ActivityhasLeaked=="False"):
                        numActivityNoLeaked=numActivityNoLeaked+1;

    # Writing LeakingReport.csv
    try:
        with open('Results/'+package+'/LeakingReport.csv', 'w') as f:
            f.write("Activity Leaked,Total Shallow Heap,Total Retained Size\n")
            if(APKhasLeaked=="True"):
                f.write(str(numLeakedActivity)+","+str(ShallowHeapTotal)+","+str(RetainedSizeTotal)+"\n")
                for line in LeakedLog:
                    f.write(str(line)+"\n")
            elif(APKhasLeaked=="False"):
                f.write("The application has no leaks!")
        f.close()
    except:
        print("Unexpected error writing LeakingReport.txt")
        raise

    # Writing ActivityReport.csv
    try:
        with open('Results/'+package+'/ActivityReport.csv', 'w') as f:
            if(APKhasLeaked=="True"):
                for line in ActivityLeakedLog:
                    f.write(str(line)+"\n")
            elif(APKhasLeaked=="False"):
                f.write("The application has no leaks! No Leak Activities are,"+str(numActivityNoLeaked))
        f.close()
    except:
        print("Unexpected error writing ActivityReport.txt")
        raise
