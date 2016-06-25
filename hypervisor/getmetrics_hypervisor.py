#!/usr/bin/python

import csv
import subprocess
import time
import os
from optparse import OptionParser
import socket

'''
this script gathers system info from /proc/ and add to daily csv file
'''

usage = "Usage: %prog [options]"
parser = OptionParser(usage=usage)
parser.add_option("-d", "--directory",
    action="store", dest="homepath", help="Directory to run from")
(options, args) = parser.parse_args()


if options.homepath is None:
    homepath = os.getcwd()
else:
    homepath = options.homepath
datadir = 'data/'

def listtocsv(lists):
    log = ''
    for i in range(0,len(lists)):
        log = log + str(lists[i])
        if(i+1 != len(lists)):
            log = log + ','
    resource_usage_file.write("%s\n"%(log))

def getindex(col_name):
    if col_name == "CPU#%":
        return 1
    elif col_name == "DiskRead#MB/s" or col_name == "DiskWrite#MB/s":
        return 2
    elif col_name == "NetworkIn#Mbps" or col_name == "NetworkOut#Mbps":
        return 3
    elif col_name == "MemUsed#MB":
        return 4

fields = []
hostname = socket.gethostname().partition(".")[0]
try:
    command = "esxtop -b -n 1 > " + os.path.join(homepath,datadir) + "esxtopOutput.txt"
    print command
    date = time.strftime("%Y%m%d")
    resource_usage_file = open(os.path.join(homepath,datadir+date+".csv"),'a+')
    numlines = len(resource_usage_file.readlines())
    metricValues = []
    proc = subprocess.Popen(command, cwd=homepath, stdout=subprocess.PIPE, shell=True)
    (out,err) = proc.communicate()
    logFile = open((os.path.join(homepath,datadir,"esxtopOutput.txt"),'r')
    content=logFile.readlines()
    metrics = content[0].split(",")
    values = content[1].split(",")
    metricList = ["timestamp", "CPU#%", "DiskRead#MB/s", "DiskWrite#MB/s", "NetworkIn#Mbps", "NetworkOut#Mbps", "MemUsed#MB"]
    for i in range(0,len(metricList)):
        metricValues.append(0)
    totalMemory = freeMemory = diskRead = diskWrite = networkTx = networkRx = cpu = 0
    timestamp = int(time.time()*1000)
    metricValues[metricList.index("timestamp")] = timestamp
    for i in range(0,len(metrics)):
        for metric in metricList:
            if metric == "MemUsed#MB":
                if "Memory\Machine MBytes" in metrics[i]:
                    values[i] = values[i].replace('"', '').strip()
                    totalMemory = totalMemory + int(values[i])
                elif "Memory\Free MBytes" in metrics[i]:
                    values[i] = values[i].replace('"', '').strip()
                    freeMemory = freeMemory + int(values[i])
                metricValues[metricList.index(metric)] = abs(totalMemory - freeMemory)
            elif metric == "DiskRead#MB/s" and "MBytes Read/sec" in metrics[i]:
                values[i] = values[i].replace('"', '').strip()
                diskRead = diskRead + float(values[i])
                metricValues[metricList.index(metric)] = diskRead
            elif metric == "DiskWrite#MB/s" and "MBytes Written/sec" in metrics[i]:
                values[i] = values[i].replace('"', '').strip()
                diskWrite = diskWrite + float(values[i])
                metricValues[metricList.index(metric)] = diskWrite
            elif metric == "NetworkOut#Mbps" and "MBits Transmitted/sec" in metrics[i]:
                values[i] = values[i].replace('"', '').strip()
                networkTx = networkTx + float(values[i])
                metricValues[metricList.index(metric)] = networkTx
            elif metric == "NetworkIn#Mbps" and "MBits Received/sec" in metrics[i]:
                values[i] = values[i].replace('"', '').strip()
                networkRx = networkRx + float(values[i])
                metricValues[metricList.index(metric)] = networkRx
            elif metric == "CPU#%" and "% Used" in metrics[i]:
                values[i] = values[i].replace('"', '').strip()
                cpu = cpu + float(values[i])
                metricValues[metricList.index(metric)] = cpu

    if(numlines < 1):
        for metric in metricList:
            if metric != "timestamp":
                groupid = getindex(metric)
                tempField = metric + "[" + hostname + "]"
                tempField = tempField + ":" + str(groupid)
                fields.append(tempField)
            else:
                fields.append(metric)
        print fields
        listtocsv(fields)
    listtocsv(metricValues)
    resource_usage_file.flush()
    resource_usage_file.close()
    print metricValues

except KeyboardInterrupt:
    print "Interrupt from keyboard"
