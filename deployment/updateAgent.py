#!/usr/bin/python

import os
import json
import subprocess
from optparse import OptionParser

usage = "Usage: %prog [options]"
parser = OptionParser(usage=usage)
parser.add_option("-t", "--agentType",
    action="store", dest="agentType", help="AgentType")
(options, args) = parser.parse_args()

if options.agentType is None:
    agentType = "proc"
else:
    agentType = options.agentType

def getTotalAgents():
    if os.path.isfile(os.path.join("InsightAgent-cleanup", "agentLookup.json")) == False:
        return 0
    with open(os.path.join("InsightAgent-cleanup", "agentLookup.json"), "r") as f:
        agentLookup = json.load(f)
    agents = 0
    for keys in agentLookup:
        if agentLookup[keys] == "1":
           agents+=1
    return agents

def isAgentDeployed(agent):
    if os.path.isdir("InsightAgent-cleanup") == True:
        return False
    if os.path.isfile(os.path.join("InsightAgent-cleanup", "agentLookup.json")) == False:
        return False
    with open(os.path.join("InsightAgent-cleanup", "agentLookup.json"), "r") as f:
        agentLookup = json.load(f)
    if agentLookup[agent] == "1":
        return True
    else:
        return False

def updateAgent():
    if os.path.isdir("InsightAgent-cleanup") == True:
        if getTotalAgents() < 2 and isAgentDeployed(agentType) == True:
            command = "sudo rm -rf insightagent* InsightAgent*\n \
                wget --no-check-certificate https://github.com/insightfinder/InsightAgent/archive/cleanup.tar.gz -O insightagent.tar.gz\n \
                tar xzvf insightagent.tar.gz\n \
                cd InsightAgent-cleanup && python deployment/checkpackages.py\n \
                sudo rm ../insightagent*\n"
        else:
            command = "wget --no-check-certificate https://github.com/insightfinder/InsightAgent/archive/cleanup.tar.gz -O insightagent.tar.gz\n \
                    tar xzvf insightagent.tar.gz\n \
                    cd InsightAgent-cleanup && python deployment/checkpackages.py\n \
                    sudo rm ../insightagent*\n"
        return command
    command = "sudo rm -rf insightagent* InsightAgent*\n \
    wget --no-check-certificate https://github.com/insightfinder/InsightAgent/archive/cleanup.tar.gz -O insightagent.tar.gz\n \
        tar xzvf insightagent.tar.gz\n \
        cd InsightAgent-cleanup && python deployment/checkpackages.py\n \
        sudo rm ../insightagent*\n"
    return command

homepath = os.getcwd()
execCommand = updateAgent()
proc = subprocess.Popen(execCommand, cwd=homepath, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
(out, err) = proc.communicate()