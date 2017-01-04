#!/usr/bin/python

from Aion.data_generation.stimulation.Garfield import Garfield
from Aion.data_generation.reconstruction import *
from Aion.data_inference.learning import HMM, ScikitLearners
from Aion.utils.data import *     # Needed for accessing configuration files
from Aion.utils.graphics import * # Needed for pretty printing
from Aion.utils.misc import *

from sklearn.metrics import *
import numpy, ghmm
import introspy # Used for analysis of introspy generated databases

import os, sys, glob, shutil, argparse, subprocess, sqlite3



def defineArguments():
    parser = argparse.ArgumentParser(prog="runExperimentI.py", description="A tool to implement the stimulation-detection feedback loop using Garfield as stimulation engine.")
    parser.add_argument("-s", "--sdkdir", help="The path to Android SDK", required=True)
    parser.add_argument("-x", "--malwaredir", help="The directory containing the malicious APK's to analyze", required=False, default=".")
    parser.add_argument("-g", "--goodwaredir", help="The directory containing the benign APK's to analyze", required=False, default=".")
    parser.add_argument("-f", "--analyzeapks", help="Whether to perform analysis on the retrieved APK's", required=False, default="no", choices=["yes", "no"])
    parser.add_argument("-t", "--analysistime", help="How long to run monkeyrunner (in seconds)", required=False, default=60)
    parser.add_argument("-v", "--vmname", help="The name of the Genymotion machine to use for analysis", required=False, default="")
    parser.add_argument("-z", "--vmsnapshot", help="The name of the snapshot to restore before analyzing an APK", required=False, default="")
    parser.add_argument("-a", "--algorithm", help="The machine learning algorithm to use for classification", required=False, default="hmm", choices=["hmm", "associative", "svm"])
    parser.add_argument("-k", "--kfold", help="Whether to use k-fold cross validation and the value of \"K\"", required=False, default=2)
    parser.add_argument("-p", "--fileextension", help="The extension of feature files", required=False, default="txt")
    parser.add_argument("-w", "--hmmtrainwith", help="Whether to train the HMM with malicious or benign instances", required=False, default="malware", choices=["malware", "goodware"])
    parser.add_argument("-l", "--hmmtracelength", help="The maximum trace length to consider during testing", required=False, default=50)
    parser.add_argument("-e", "--hmmthreshold", help="The likelihood threshold to apply during testing", required=False, default=-500)
    return parser

def main():
    try:
        argumentParser = defineArguments()
        arguments = argumentParser.parse_args()
        prettyPrint("Welcome to the \"Aion\"'s experiment I")

        # Some sanity checks
        if not os.path.exists(arguments.sdkdir):
             prettyPrint("Unable to locate the Android SDK. Exiting", "error")
             return False
 
        iteration = 1 # Initial values
        currentMetrics = {"accuracy": 0.0, "recall": 0.0, "specificity": 0.0, "precision": 0.0, "fscore": 0.0}
        previousMetrics = {"accuracy": 0.0, "recall": 0.0, "specificity": 0.0, "precision": 0.0, "fscore": 0.0}


        while currentMetrics["fscore"] >= previousMetrics["fscore"]:
            prettyPrint("Experiment I: iteration #%s" % iteration, "info2")
            if arguments.analyzeapks == "yes" or iteration >= 2:
                # Define paths to Android SDK tools
                monkeyRunnerPath = arguments.sdkdir + "/tools/monkeyrunner"
                adbPath = arguments.sdkdir + "/platform-tools/adb"

                # Retrieve malware APK's
                malAPKs = glob.glob("%s/*.apk" % arguments.malwaredir)
                if len(malAPKs) < 1:
                    prettyPrint("Could not find any malicious APK's under \"%s\"" % arguments.malwaredir, "warning")
                else:
                    prettyPrint("Successfully retrieved %s malicious instances from \"%s\"" % (len(malAPKs), arguments.malwaredir))
                # Retrieve goodware APK's
                goodAPKs = glob.glob("%s/*.apk" % arguments.goodwaredir)
                if len(goodAPKs) < 1:
                    prettyPrint("Could not find any malicious APK's under \"%s\"" % arguments.goodwaredir, "warning")
                else:
                    prettyPrint("Successfully retrieved %s malicious instances from \"%s\"" % (len(goodAPKs), arguments.goodwaredir))

                allAPKs = malAPKs + goodAPKs
                if len(allAPKs) < 1:
                    prettyPrint("Could not find any APK's under \"%s\". Exiting" % arguments.indir, "error")
                    return False

                genyProcess = None # TODO: A handle to the genymotion player process
                for path in allAPKs:
                    # 1. Statically analyze the APK using androguard
                    APKType = "malware" if path in malAPKs else "goodware"
                    currentAPK = Garfield(path, APKType)
 
                    if verboseON():
                        prettyPrint("Analyzing APK: \"%s\"" % path, "debug")

                    # 1.a. Analyze APK
                    if not currentAPK.analyzeAPK():
                        prettyPrint("Analysis of APK \"%s\" failed. Skipping" % path, "warning")
                        continue
                    
                    # 1.b. Check whether trace is saved from previous runs/iterations
                    if os.path.exists("%s/files/tmp/%s_%s.trace" % (getProjectDir(), currentAPK.APK.package, currentAPK.APKType)):
                        prettyPrint("Found a saved trace for %s. Skipping analysis" % currentAPK.APK.package, "info2")
                        continue

                    # 2. Generate Monkeyrunner script
                    if not currentAPK.generateRunnerScript(int(arguments.analysistime)):
                        prettyPrint("Generation of \"Monkeyrunner\" script failed. Skipping", "warning")
                        continue

                    # Define frequently-used commands
                    vboxRestoreCmd = ["vboxmanage", "snapshot", arguments.vmname, "restore", arguments.vmsnapshot]
                    vboxPowerOffCmd = ["vboxmanage", "controlvm", arguments.vmname, "poweroff"]
                    genymotionStartCmd = ["/opt/genymobile/genymotion/player", "--vm-name", arguments.vmname]
                    monkeyRunnerCmd = [monkeyRunnerPath, currentAPK.runnerScript]
                    adbPullCmd = [adbPath, "pull", "/data/data/%s/databases/introspy.db" % str(currentAPK.APK.package)]

                    # 3. Prepare the Genymotion virtual Android device
                    # 3.a. Restore vm to given snapshot
                    if verboseON():
                        prettyPrint("Restoring snapshot \"%s\"" % arguments.vmsnapshot, "debug")
                    result = subprocess.Popen(vboxRestoreCmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).communicate()[0]
                    attempts = 1
                    while result.lower().find("error") != -1:
                        print result
                        # Retry restoring snapshot for 10 times and then exit
                        if attempts == 10:
                            prettyPrint("Failed to restore snapshot \"%s\" after 10 attempts. Exiting" % arguments.vmsnapshot, "error")
                            return False
                        prettyPrint("Error encountered while restoring the snapshot \"%s\". Retrying ... %s" % (arguments.vmsnapshot, attempts), "warning")
                        # Make sure the virtual machine is switched off for, both, genymotion and virtualbox
                        if genyProcess:
                            genyProcess.kill()
                        subprocess.Popen(vboxPowerOffCmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
                        # Now attempt restoring the snapshot
                        result = subprocess.Popen(vboxRestoreCmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).communicate()[0]
                        attempts += 1
                        time.sleep(1)

                    # 3.b. Start the Genymotion Android virtual device
                    if verboseON():
                        prettyPrint("Starting the Genymotion machine \"%s\"" % arguments.vmname, "debug")

                    genyProcess = subprocess.Popen(genymotionStartCmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
                    if verboseON():
                        prettyPrint("Waiting for machine to boot ...", "debug")
                    time.sleep(10)

                    # 4. Run the generated script
                    prettyPrint("Launching the fuzzing script \"%s\"" % currentAPK.runnerScript)
                    result = subprocess.Popen(monkeyRunnerCmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).communicate()[0]
                    while result.lower().find("socket") != -1:
                        prettyPrint("An error occured while running the monkey script. Re-running", "warning")
                        result = subprocess.Popen(monkeyRunnerCmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).communicate()[0]
                        
                    # 5. Download the introspy.db
                    #x = raw_input("continue? ")
                    subprocess.Popen(adbPullCmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).communicate()[0]
                    # 6. Analyze the downloaded database
                    # 6.a. Check that the database exists and is not empty
                    if os.path.exists("introspy.db"):
                        if int(os.path.getsize("introspy.db")) == 0:
                            prettyPrint("The database generated by Introspy is empty. Skipping", "warning")
                            subprocess.Popen(vboxPowerOffCmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
                            genyProcess.kill()
                            continue
                    # Last line of defense
                    try:
                        db = introspy.DBAnalyzer("introspy.db", "foobar")
                    except sqlite3.OperationalError as sql:
                        prettyPrint("The database generated by Introspy is probably empty. Skipping", "warning")
                        continue

                    trace = db.get_traced_calls_as_JSON()

                    # 7. Write trace to malware/goodware dir
                    # 7.a. Get a handle
                    if currentAPK.APKType == "malware": 
                        traceFile = open("%s/%s_%s.json" % (arguments.malwaredir, currentAPK.APK.package, currentAPK.APKType), "w")
                    else:
                        traceFile = open("%s/%s_%s.json" % (arguments.malwaredir, currentAPK.APK.package, currentAPK.APKType), "w")
                    # 7.b. Write content
                    traceFile.write(trace)
                    traceFile.close()

                    # 7.c. Introspy's HTML report
                    html = introspy.HTMLReportGenerator(db, "foobar") # Second arguments needs to be anythin but ""/None
                    if currentAPK.APK.package == "malware":
                        html.write_report_to_directory("%s/%s" % (arguments.malwaredir, currentAPK.APK.package))
                    else:
                        html.write_report_to_directory("%s/%s" % (arguments.goodwaredir, currentAPK.APK.package))
                
                    # 7.d. Extract and save numerical features for SVM's and Trees
                    features = extractAndroguardFeatures(path) + extractIntrospyFeatures(traceFile)
                    if currentAPK.APKType == "malware":
                        featuresFile = open("%s/%s.%s" % (arguments.malwaredir, currentAPK.APK.package, arguments.fileextension), "w")
                    else:
                        featuresFile = open("%s/%s.%s" % (arguments.goodwaredir, currentAPK.APK.package, arguments.fileextension), "w")

                    featuresFile.write("%s\n" % str(features)[1:-1])
                    featuresFile.close()

                    prettyPrint("Done analyzing \"%s\"" % currentAPK.APK.package)
                    
                    # Delete old introspy.db file
                    os.remove("introspy.db")
 
                    # Shutdown the genymotion machine
                    subprocess.Popen(vboxPowerOffCmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
                    genyProcess.kill()

            ####################################################################
            # Load the JSON  and feature files as traces before classification #
            ####################################################################
            if arguments.algorithm == "hmm":
                if arguments.hmmtrainwith == "malware":
                    allJSONFiles = glob.glob("%s/*.json" % arguments.malwaredir)
                    allJSONFiles += glob.glob("%s/*.json" % arguments.goodwaredir)
                else:
                    allJSONFiles = glob.glob("%s/*.json" % arguments.goodwaredir)
                    allJSONFiles += glob.glob("%s/*.json" % arguments.malwaredir)

                if len(allJSONFiles) < 1:
                    prettyPrint("Unable to retrieve any JSON files from \"%s\" or \"%s\". Exiting" % (arguments.malwaredir, arguments.goodwaredir), "error")
                    return False
                else:
                    prettyPrint("Successfully retrieved %s JSON files" % len(allJSONFiles))

                # 1. Parse and retrieve comma-separated traces for all traces
                allTraces = Trace.loadJSONTraces(allJSONFiles, "list")
                if len(allTraces) != len(allJSONFiles):
                    prettyPrint("The number of parsed traces does not match that of JSON files", "warning")
                    answer = raw_input("Continue? [Y/n] ")
                    if answer.lower() == "n":
                        return False
            else:
                # Load numerical features
                allFeatureFiles = glob.glob("%s/*.%s" % (arguments.malwaredir, arguments.fileextension)) + glob.glob("%s/*.%s" % (arguments.goodwaredir, arguments.fileextension))
                
            #######################
            # Hidden Markov Model #
            #######################
            if arguments.algorithm == "hmm":
                prettyPrint("Classifying using HMM and training with \"%s\" instances" % arguments.hmmtrainwith)

                # Build X and y from "allTraces"
                X = [t[0] for t in allTraces]
                y = [t[1] for t in allTraces]

                # Perform cross validation predicted
                predicted = HMM.cross_val_predict(X, y, arguments.hmmtracelength, arguments.hmmthreshold, int(arguments.kfold), arguments.hmmtrainwith)
                # Calculate the performance metrics
                metrics = ScikitLearners.calculateMetrics(y, predicted)
            
            ###########################
            # Support Vector Machines #
            ###########################
            elif arguments.algorithm == "svm":
                prettyPrint("Classifying using Support Vector Machines")

                X, y = [], []
                for f in allFeatureFiles:
                    X.append(Numerical.loadNumericalFeatures(f))
                    if f.find("malware") != -1:
                        y.append(1)
                    else:
                        y.append(0)

                prettyPrint("Successfully loaded %s feature files" % len(X))
                predicted = ScikitLearners.predictKFoldSVM(X, y, kfold=int(arguments.kfold))
                metrics = ScikitLearners.calculateMetrics(y, predicted)

            ##################
            # Decision Trees #
            ##################
            elif arguments.algorithm == "tree":
                prettyPrint("Classifying using Decision Trees")

                X, y = [], []
                for f in allFeatureFiles:
                    X.append(Numerical.loadNumericalFeatures(f))
                    if f.find("malware") != -1:
                        y.append(1)
                    else:
                        y.append(0)

                prettyPrint("Successfully loaded %s feature files" % len(X))
                predicted = ScikitLearners.predictKFoldTree(X, y, kfold=int(arguments.kfold))
                metrics = ScikitLearners.calculateMetrics(y, predicted)

            # The average metrics
            prettyPrint("Metrics using %s-fold cross validation and %s" % (arguments.kfold, arguments.algorithm), "output")
            prettyPrint("Accuracy: %s" % str(metrics["accuracy"]), "output")
            prettyPrint("Recall: %s" % str(metrics["recall"]), "output")
            prettyPrint("Specificity: %s" % str(metrics["specificity"]), "output")
            prettyPrint("Precision: %s" % str(metrics["precision"]), "output")
            prettyPrint("F1 Score: %s" %  str(metrics["f1score"]), "output")

            # Save correctly-classified instances for future use
            for index in range(len(y)):
                if predicted[index] == y[index]:
                    # Store the instance's representation i.e. trace/feature vector
                    if arguments.algorithm == "hmm":
                       trace = allTraces[index]
                       traceFile = open("%s/%s.%s" % (arguments.malwaredir, trace[2], arguments.fileextension), "w") if trace[1] == 1 else open("%s/%s.%s" % (arguments.goodwaredir, trace[2], arguments.fileextension), "w")
                       traceFile.write(trace[0])
                       traceFile.close()
                    else:
                        numFile = open(allFeatureFiles[index], "w")
                        numFile.write(X[index])
                        numFile.close()
                else:
                    # Remove any previously-stored representation 
                    if arguments.algorithm == "hmm":
                        traceFile = "%s/%s.%s" % (arguments.malwaredir, allTraces[index][2], arguments.fileextension) if allTraces[index][1] == 1 else "%s/%s.%s" % (arguments.goodwaredir, allTraces[index][2], arguments.fileextension)
                        if os.path.exists(traceFile):
                            os.unlink(traceFile)
                    else:
                        if os.path.exists(allFeatureFiles[index]):
                            os.unlink(allFeatureFiles[index])

            # Swapping metrics
            previousMetrics = currentMetrics
            for m in metrics:
                metrics[m] = metrics[m]/float(arguments.kfold)
            currentMetrics = metrics
            # Increment the iteration for further analysis
            iteration += 1
            
    except Exception as e:
        prettyPrintError(e)
        return False
    
    prettyPrint("Good day to you ^_^")
    return True

if __name__ == "__main__":
    main() 
