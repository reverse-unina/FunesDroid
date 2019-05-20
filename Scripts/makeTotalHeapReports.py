import os
import csv
import sys

import AndroLeakUtil

# CORPO DELLO SCRIPT
li = sys.argv
li.pop(0)
if (len(li)==1):
    FOLDER=str(li[0])
else:
    FOLDER="Results"
    print("Warning. Working with default values")

print("Creating LeakingReport.csv and ActivityReport.csv")
for x in os.listdir(FOLDER+"/"):
    if(os.path.isdir(FOLDER+"/"+x)):
        package=x;
        AndroLeakUtil.makeLeakingReport(package);

print("Creating TotalHeap.csv and TotalHeapFinalReport.csv")
AndroLeakUtil.makeTotalHeapCSV()
AndroLeakUtil.makeTotalHeapFinalReport()
AndroLeakUtil.makeAndroLeakReport()

cmd="python aggregaInfoActivity.py";
os.system(cmd);

print("Execution Completed.")
