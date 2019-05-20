import os
import shutil
import sys

def createOutputDirectory(package,activity,REPETITON):
    directory="MatlabFormat/"+package+"/"+activity+"/"+REPETITON+"/"
    if not os.path.exists(directory):
        os.makedirs(directory)

def copyDumpLogFile(package,activity,FOLDER,REPETITON):
    dumpfile=FOLDER+"/"+package+"/"+activity+"/DumpLog.txt"
    destination="MatlabFormat/"+package+"/"+activity+"/"+REPETITON+"/DumpLog.txt"
    if os.path.isfile(dumpfile):
        shutil.copyfile(dumpfile,destination)

def copyGCfile(package,FOLDER,REPETITON):
    GCfile=FOLDER+"/"+package+"/GClogs_from_logcat.txt"
    destination="MatlabFormat/"+package+"/"+activity+"/"+REPETITON+"/GClogs_from_logcat.txt"
    if os.path.isfile(GCfile):
        shutil.copyfile(GCfile,destination)

def copyCSVfiles(package,activity,FOLDER,REPETITON): 
    csvfile_name=package+"_0_before_"+activity+"_conv.csv"
    csvfile=FOLDER+"/"+package+"/"+activity+"/"+csvfile_name
    destination="MatlabFormat/"+package+"/"+activity+"/"+REPETITON+"/"+csvfile_name
    if os.path.isfile(csvfile):
        shutil.copyfile(csvfile,destination)
    for i in range(1,10):
        k=i*10
        csvfile_name=package+"_"+str(k)+"_after_"+activity+"_conv.csv"
        csvfile=FOLDER+"/"+package+"/"+activity+"/"+csvfile_name
        destination="MatlabFormat/"+package+"/"+activity+"/"+REPETITON+"/"+csvfile_name
        if os.path.isfile(csvfile):
            shutil.copyfile(csvfile,destination)
    csvfile_name=package+"_100_after_"+activity+"_conv.csv"
    csvfile=FOLDER+"/"+package+"/"+activity+"/"+csvfile_name
    csvfile_name=package+"_99_after_"+activity+"_conv.csv"
    destination="MatlabFormat/"+package+"/"+activity+"/"+REPETITON+"/"+csvfile_name
    if os.path.isfile(csvfile):
        shutil.copyfile(csvfile,destination)

DUMP_NUMB=60
def copyCSVfiles_2(package,activity,FOLDER,REPETITON): 
    csvfile_name=package+"_0_before_"+activity+"_conv.csv"
    csvfile=FOLDER+"/"+package+"/"+activity+"/"+csvfile_name
    destination="MatlabFormat/"+package+"/"+activity+"/"+REPETITON+"/"+csvfile_name
    if os.path.isfile(csvfile):
        shutil.copyfile(csvfile,destination)
    for i in range(1,DUMP_NUMB+1):
        k=i
        csvfile_name=package+"_"+str(k)+"_after_"+activity+"_conv.csv"
        csvfile=FOLDER+"/"+package+"/"+activity+"/"+csvfile_name
        destination="MatlabFormat/"+package+"/"+activity+"/"+REPETITON+"/"+csvfile_name
        if os.path.isfile(csvfile):
            shutil.copyfile(csvfile,destination)
        
# CORPO DELLO SCRIPT
li = sys.argv
li.pop(0)
if (len(li)==2):
    FOLDER=str(li[0])
    REPETITON=str(li[1])
else:
    FOLDER="Results"
    REPETITON="1"
    print("Warning. Working with default values")

for x in os.listdir(FOLDER+"/"):
    if(os.path.isdir(FOLDER+"/"+x)):
        package=x
        for y in os.listdir(FOLDER+"/"+package+"/"):
            if(os.path.isdir(FOLDER+"/"+package+"/"+y)):
                activity=y
                print("Creating output directory for "+activity)
                createOutputDirectory(package,activity,REPETITON)
                print("Copying DumpLog.txt file")
                copyDumpLogFile(package,activity,FOLDER,REPETITON)
                print("Copying GC file")
                copyGCfile(package,FOLDER,REPETITON)
                print("Copying CSV files")
                copyCSVfiles_2(package,activity,FOLDER,REPETITON)
