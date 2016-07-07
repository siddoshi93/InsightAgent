#!/usr/bin/python

import os
import json
from optparse import OptionParser

homepath = os.getenv("INSIGHTAGENTDIR")
usage = "Usage: %prog [options]"
parser = OptionParser(usage=usage)
parser.add_option("-r", "--reporting_interval",
    action="store", dest="reporting_interval", help="Reporting interval in minute")
parser.add_option("-t", "--agentType",
    action="store", dest="agentType", help="AgentType")
(options, args) = parser.parse_args()

if options.agentType is None:
    agentType = "proc"
else:
    agentType = options.agentType

if options.reporting_interval is None:
    reporting_interval = "5"
else:
    reporting_interval = options.reporting_interval
if homepath is None:
    homepath = os.getcwd()

datadir = agentType+'/data/'
deltaFields = ["CPU#%", "DiskRead#MB", "DiskWrite#MB", "NetworkIn#MB", "NetworkOut#MB"]
procFields = ["CPU#%", "DiskRead#MB", "DiskWrite#MB", "DiskUsed#MB", "NetworkIn#MB", "NetworkOut#MB", "MemUsed#MB"]
cadvisorFields = ["CPU#%"]
cgroupFields = ["CPU#%", "DiskRead#MB", "DiskWrite#MB", "NetworkIn#MB", "NetworkOut#MB", "MemUsed#MB"]
dockerRemoteApiFields = ["CPU#%", "DiskRead#MB", "DiskWrite#MB", "NetworkIn#MB", "NetworkOut#MB", "MemUsed#MB"]

#update endtime in config file
def update_configs(reporting_interval,prev_endtime,keep_file_days):
    config = {
        'reporting_interval' : reporting_interval,
        'prev_endtime' : prev_endtime,
        'keep_file_days' : keep_file_days,
        'delta_fields' : deltaFields
    }
    with open(os.path.join(homepath, datadir, "reporting_config.json"),"w") as f:
        json.dump(config, f)

def updateReportingConfig():
    if os.path.isfile(os.path.join(homepath, datadir, "config.json")) == True:
        return
    global agentType
    if agentType == "proc":
        fields = procFields
    elif agentType == "cadvisor":
        fields = cadvisorFields
    elif agentType == "cgroup":
        fields = cgroupFields
    elif agentType == "docker_remote_api":
        fields = dockerRemoteApiFields
    else:
        fields = ""
    reportingConfig = {'reportingFields' : fields}
    with open(os.path.join(homepath, datadir, "config.json"),"w") as conf:
        json.dump(reportingConfig, conf)

update_configs(reporting_interval,"0","5")
updateReportingConfig()
