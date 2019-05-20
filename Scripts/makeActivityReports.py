import sys
import os
import AndroLeakUtil

# CORPO DELLO SCRIPT
li = sys.argv
li.pop(0)
if (len(li)==1):
    FOLDER=str(li[0])
else:
    FOLDER="Results"
    print("Warning. Working with default values")

for x in os.listdir(FOLDER+"/"):
    if(os.path.isdir(FOLDER+"/"+x)):
        package=x;
        AndroLeakUtil.makeLeakingReport(package);
        AndroLeakUtil.makeActivityReport(FOLDER,package);

print("Completed.")
