FunesDroid 2022


The goal of the FunesDroid tool is to check whether the Activity classes of an analyzed Android app expose or not memory leaks tied to the Activity lifecycle.

FunesDroid is able to execute automatically the following test on the input apks:
- Double Orientation Change (DOC), corresponding to a double rotation of the device, from landscape to portrait and finally to landscape or, equivalently, from portrait to landscape and, finally, to portrait. Each of these orientation changes exercises the EL loop, since the running Activity is destroyed and recreated in order to fit the rotated device layout. 
- Background-Foreground (BF), corresponding to a sequence of events exercising the VL loop. For example, a possible sequence includes the click on the Back button of the device (that may bring the running Activity to the Stopped state), followed by the selection of the same Activity from the list of the recently stopped one. This last event causes the restarting of the Activity, without the need to redraw its graphical layout.
- Semi-Transparent Activity Intent and back (STAI), corresponding to  a sequence of events exercising the VL loop. This sequence bring the running Activity to the paused state, and successively to the running state.

The three considered lopps are the following:
- Entire Loop (EL) of an Activity consists in the Resumed-Paused-Stopped-Destroyed-Created-Started-Resumed sequence of states. This loop can be exercised by events that cause a configuration change, e.g. an orientation change of the screen, that destroys the Activity instance and then recreates it according to the new configuration; 
- Visible Loop (VL) corresponds to the Resumed-Paused-Stopped-Started-Resumed sequence of states during which the Activity is hidden and then made visible again. There are several event sequences able to stop and restart an Activity, e.g. turning off and on the screen or putting the app in background and then in foreground again through the Overview or Home buttons;
- Foreground Loop (FL) of an Activity involves the Resumed-Paused-Resumed state sequence.
The transition Resumed-Paused can be triggered by opening non full-sized elements such as modal dialogs or semi-transparent activities that occupy the foreground while the Activity is still visible in background. To trigger the transition Paused-Resumed the user should discard this element.

Prerequisites:
- Pyhton interpreter (we used Python 3.7.3 for Windows)
- Android sdk (we used Android 7.1.1 - API 25)
- Both python.exe path and the executable paths of the Android Sdk are in the system path (e.g. tools and platform-tools)

In order to execute the tool on a sample of Android applications, we have provided them in the SampleAPKs folder.
In order to execute the tool in the experimental modality, the following steps have to be executed:

1) Create an InputAPKs/ folder in this directory. 

2) Add the apk files do you want to test in the InputAPKs/ directory.

3) Launch an Android Virtual Device (or real device) and get the device name throgh the system command "adb devices".
Be sure that the Emulator data have been wiped. The default name for Android Virtual Devices is "emulator-5554" 

4) Edit launchexp.py in the following fields:
	- set the Lifecycle Event Sequences (LES) to be tested (a single value or a list of values). For example:
		les=["doc","bf","stai"]
	- set the number of times the chosen LES will be repeated before the evaluation of memory leaks (a single value or a list of values). For example:
		nevent=[1,2,10]
	- set the waiting time (in seconds) between the execution of the last LES, the execution of the garbage collector and the memory dumping (a single value or a list of values). For example:
		wtime=[1,2,5]
	- set the emulator name. For example "emulator-5554" in the following line:
		cmd = "python AndroLeak.py emulator-5554 "+event+" "+str(number)+" "+str(t)

5) Execute launchexp.py from the command line. A set of experiments corresponding to all the possible combinations of LES, nevent and wtime values will be executed sequentially for each of the apks included in the InputAPKs/ folder.

6) The obtained results are in the Results folder. In details, a subfolder for each tested application and configuration will be created. The name of the folder includes information about the executed tests. For example:
	- the folder "net.programmierecke.radiodroid2_doc_N1_t1_1559297752" contains the results of the tests executed on the application "net.programmierecke.radiodroid2" corresponding to the execution of N=1 repetitions of doc sequences of events with a waiting time t=1 second. The number "1559297752" indicates the time of the execution of the experiment and is useful to distinguish between different identical tests.
In the folder you can find:
	- the ActivityReport.csv file, reporting the list of the leaked Activities.
	- the LeakReport.csv file, reporting the list of all the leaked objects, the number of their instances, the amount of leaked memory, for each of the tested Activity classes for which at least a leak were found.
	- other files, reporting other details of the carried out tests, such as logcat files, a summary of the executed tests, the hprof files collected during the tests.
		
Important. During its execution, AndroLeak creates many temporary files. They should be automatically removed at the end of the experiments, but it is possible that they remain on the disk, in some systems. In these cases, you should manually delete them via operating system utilities.
 

