import sys
import os
import csv

# CORPO DELLO SCRIPT
li = sys.argv
li.pop(0)
if (len(li)==1):
    FOLDER=str(li[0])
else:
    FOLDER="Results"
    print("Warning. Working with default values")

Result = []
numOfNoLeakedActivities=0
for x in os.listdir(FOLDER+"/"):
    if(os.path.isdir(FOLDER+"/"+x)):
        package=x
        f=FOLDER+"/"+package+"/ActivityReport.csv"
        with open(f) as csvfile: # Open the CSV file
            ActivityhasLeaked = "False"
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            #next(spamreader,None)
            for row in spamreader: # For each row
                if("no leaks!" in row[0]):
                    numOfNoLeakedActivities=numOfNoLeakedActivities+int(row[1]);
                    continue
                if("Leaked Activity" in row[0]):
                    continue
                print(row)
                Result.append(package+"/."+str(row[0])+","+str(row[1])+","+str(row[2]));

# Writing LeakingReport.csv
try:
    with open('AggregatoActivity.csv', 'w') as f:
        for line in Result:
            f.write(str(line)+"\n")
        if not Result:
            f.write("There is no Activity Leaked\n")
        f.close()
except:
    raise

print("Number of NoLeaked Activities:" + str(numOfNoLeakedActivities))
print("Completo!")

