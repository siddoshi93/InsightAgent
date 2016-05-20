#!/bin/python
import subprocess
import os
from optparse import OptionParser
import linecache
import json
import time
import datetime

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

def getindex(colName):
    if colName == "CPU_utilization#%":
        return 1
    elif colName == "DiskRead#MB" or colName == "DiskWrite#MB":
        return 2
    elif colName == "NetworkIn#MB" or colName == "NetworkOut#MB":
        return 3
    elif colName == "MemUsed#MB":
        return 4

def isJson(jsonString):
    try:
	jsonObject = json.loads(jsonString)
	print jsonObject['read']
    except ValueError, e:
	return False
    except TypeError, e:
	return False
    return True

def update_docker():
    global dockers

    proc = subprocess.Popen(["docker ps | awk '{if(NR!=1) print $NF}'"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    dockers = out.split("\n")
    cronfile = open(os.path.join(homepath,datadir+"getmetrics_docker.sh"),'w')
    cronfile.write("#!/bin/sh\nDATADIR='data/'\ncd $DATADIR\n")
    containerCount = 0
    for container in dockers:
	if container == "":
	    continue
        containerCount+=1
    	command = "echo -e \"GET /containers/"+container+"/stats?stream=0 HTTP/1.1\\r\\n\" | nc -U /var/run/docker.sock > stat"+container+".txt & PID"+str(containerCount)+"=$!"
	cronfile.write(command+"\n")
    for i in range(1,containerCount+1):
	cronfile.write("wait $PID"+str(i)+"\n")
    cronfile.close()
    os.chmod(os.path.join(homepath,datadir+"getmetrics_docker.sh"),0755)
 
def getmetrics():
    global dockers

    try:
	while True:
	    for i in range(len(dockers)-1):
		filename = "stat%s.txt"%dockers[i]
		statsFile = open(os.path.join(homepath,datadir+filename),'r')
                data = statsFile.readlines()
		for eachline in data:
		    if isJson(eachline) == True:
			metricData = json.loads(eachline)
			break
	    	timestamp = metricData['read'][:19]
		timestamp =  int(time.mktime(datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S").timetuple()))
		networkRx = float(metricData['network']['rx_bytes']/(1024*1024)) #MB
		networkTx = float(metricData['network']['tx_bytes']/(1024*1024)) #MB
		cpu = float(metricData['cpu_stats']['cpu_usage']['total_usage'])
		memUsed = float(metricData['memory_stats']['usage']/(1024*1024)) #MB
		diskRead = float(metricData['blkio_stats']['io_service_bytes_recursive'][0]['value']/(1024*1024)) #MB 
		diskWrite = float(metricData['blkio_stats']['io_service_bytes_recursive'][1]['value']/(1024*1024)) #MB
		log = str(timestamp) + "," + str(cpu) + "," + str(diskRead) + "," + str(diskWrite) + "," + str(networkRx) + "," + str(networkTx) + "," + str(memUsed)
		print log
		date = time.strftime("%Y%m%d")
		csvFile = open(os.path.join(homepath,datadir+date+dockers[i]+".csv"), 'a+')
            numlines = len(csvFile.readlines())
            if(numlines < 1):
                fields = ["timestamp","CPU_utilization#%","DiskRead#MB","DiskWrite#MB","NetworkIn#MB","NetworkOut#MB","MemUsed#MB"]
                fieldnames = fields[0]
                host = dockers[i]
		for j in range(1,len(fields)):
		    if(fieldnames != ""):
			fieldnames = fieldnames + ","
		    groupid = getindex(fields[j])
		    fieldnames = fieldnames+fields[j] + "[" +host+"]"+":"+str(groupid)
		csvFile.write("%s\n"%(fieldnames))
	    csvFile.write("%s\n"%(log))
	    csvFile.flush()
	    csvFile.close()
            break
    except KeyboardInterrupt:
	print "Keyboard Interrupt"
 
try:
    update_docker()
    proc = subprocess.Popen([os.path.join(homepath,datadir+"getmetrics_docker.sh")], cwd=homepath, stdout=subprocess.PIPE, shell=True)
    (out,err) = proc.communicate()
    getmetrics()
except KeyboardInterrupt:
    print "Interrupt from keyboard"

 
