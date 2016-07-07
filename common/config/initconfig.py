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

update_configs(reporting_interval,"0","5")
