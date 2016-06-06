#!/usr/bin/python
import linecache
import json
import csv
import subprocess
import time
import os
import socket
from optparse import OptionParser

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

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def listtocsv(lists):
    log = ''
    for i in range(0,len(lists)):
        log = log + str(lists[i])
        if(i+1 != len(lists)):
            log = log + ','
    resource_usage_file.write("%s\n"%(log))

def update_results(lists):
    with open(os.path.join(homepath,datadir+"previous_results.json"),'w') as f:
        json.dump(lists,f)

def init_previous_results():
    first_result = {}
    timestampRead = False
    serverType = ["rubis_apache", "rubis_db"]
    for server in serverType:
        for eachfile in filenames:
            tempfile = eachfile.split(".")
    	    correctFile = tempfile[0]+"_"+server+"."+tempfile[1]
	    if(eachfile == "timestamp.txt" and timestampRead == False):
		correctFile = eachfile
		timestampRead = True
	    elif(eachfile == "timestamp.txt"):
		continue
	    txt_file = open(os.path.join(homepath,datadir,correctFile))
	    lines = txt_file.read().split("\n")
	    for eachline in lines:
		tokens = eachline.split("=")
		if(len(tokens) == 1):
		    continue
		if(server == "rubis_apache" and correctFile != "timestamp.txt"):
		    tokens[0] = tokens[0] + "#MB[Web_" + ipAddress + "]"
		    tokens[1] = float(float(tokens[1])/(1024*1024))
		elif(server == "rubis_db" and correctFile != "timestamp.txt"):
		    tokens[0] = tokens[0] +"#MB[DB_" + ipAddress + "]"
		    tokens[1] = float(float(tokens[1])/(1024*1024))
		first_result[tokens[0]] = tokens[1]

    update_results(first_result)
    time.sleep(1)
    proc = subprocess.Popen([os.path.join(homepath,"cgroup/getmetrics_cgroup.sh")], cwd=homepath, stdout=subprocess.PIPE, shell=True)
    (out,err) = proc.communicate()

def get_previous_results():
    with open(os.path.join(homepath,datadir+"previous_results.json"),'r') as f:
        return json.load(f)

def check_delta(field):
    deltaFields = ["DiskRead", "DiskWrite", "NetworkIn", "NetworkOut"]
    for eachfield in deltaFields:
        if(eachfield in field):
            return True
    return False

def calculate_delta(fieldname,value):
    previous_result = get_previous_results()
    delta = float(value) - previous_result[fieldname]
    delta = abs(delta)
    return round(delta,4)

fields = []
filenames = ["timestamp.txt","diskmetricsread.txt","diskmetricswrite.txt","networkmetrics.txt","memmetrics.txt"]
try:
    date = time.strftime("%Y%m%d")
    resource_usage_file = open(os.path.join(homepath,datadir+date+".csv"),'a+')
    numlines = len(resource_usage_file.readlines())
    values = []
    dict = {}
    timestampread = False
    ipAddress = get_ip_address()
    proc = subprocess.Popen([os.path.join(homepath,"cgroup/getmetrics_cgroup.sh")], cwd=homepath, stdout=subprocess.PIPE, shell=True)
    (out,err) = proc.communicate()
    print out
    print err

    if(os.path.isfile(homepath+"/"+datadir+"previous_results.json") == False):
        init_previous_results()

    serverType = ["rubis_apache", "rubis_db"]
    for server in serverType:
	tokens = []
	for eachfile in filenames:
	    tempfile = eachfile.split(".")
	    correctFile = tempfile[0]+"_"+server+"."+tempfile[1]
	    if(eachfile == "timestamp.txt" and timestampread == False):
		correctFile = eachfile
		timestampread = True
	    elif(eachfile == "timestamp.txt"):
		continue
	    print correctFile
	    txt_file = open(os.path.join(homepath,datadir,correctFile))
	    lines = txt_file.read().split("\n")
	    for eachline in lines:
		tokens = eachline.split("=")
		if(len(tokens) == 1):
		    continue
		if(server == "rubis_apache" and correctFile != "timestamp.txt"):
		    tokens[0] = tokens[0] + "#MB[Web_" + ipAddress + "]"
		    tokens[1] = float(float(tokens[1])/(1024*1024))
		elif(server == "rubis_db" and correctFile != "timestamp.txt"):
		    tokens[0] = tokens[0] +"#MB[DB_" + ipAddress + "]"
		    tokens[1] = float(float(tokens[1])/(1024*1024))
		fields.append(tokens[0])
		if(check_delta(tokens[0]) == True):
		    print "Delta value"
		    deltaValue = calculate_delta(tokens[0], tokens[1])
		    valuetoappend = "%.4f" %deltaValue
		    values.append(valuetoappend)
		else:
		    if(tokens[0] == "timestamp"):
			values.append(tokens[1])
		    else:
			valuetoappend = "%.4f" %tokens[1]
			values.append(valuetoappend)
		dict[tokens[0]] = float(tokens[1])
    if(numlines < 1):
	listtocsv(fields)
    listtocsv(values)
    resource_usage_file.flush()
    resource_usage_file.close()

except KeyboardInterrupt:
    print "Interrupt from keyboard"
