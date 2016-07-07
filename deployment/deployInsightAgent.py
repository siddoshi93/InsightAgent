#!/usr/bin/python

import argparse
import getpass
import os
import sys
import subprocess

class deployInsightAgent:

    def get_args(self):
        parser = argparse.ArgumentParser(description='Script retrieves arguments for insightfinder agent.')
        parser.add_argument('-i', '--PROJECT_NAME_IN_INSIGHTFINDER', type=str,
                            help='Project Name registered in Insightfinder', required=True)
        parser.add_argument('-n', '--USER_NAME_IN_HOST', type=str, help='User Name in Hosts', required=True)
        parser.add_argument('-u', '--USER_NAME_IN_INSIGHTFINDER', type=str, help='User Name in Insightfinder',
                            required=True)
        parser.add_argument('-k', '--LICENSE_KEY', type=str, help='License key for the user', required=True)
        parser.add_argument('-s', '--SAMPLING_INTERVAL_MINUTE', type=str, help='Sampling Interval Minutes',
                            required=True)
        parser.add_argument('-r', '--REPORTING_INTERVAL_MINUTE', type=str, help='Reporting Interval Minutes',
                            required=True)
        parser.add_argument('-t', '--AGENT_TYPE', type=str,
                            help='Agent type: proc or cadvisor or docker_remote_api or cgroup or daemonset',
                            choices=['proc', 'cadvisor', 'docker_remote_api', 'cgroup', 'daemonset'], required=True)
        args = parser.parse_args()
        projectName = args.PROJECT_NAME_IN_INSIGHTFINDER
        user = args.USER_NAME_IN_HOST
        userInsightfinder = args.USER_NAME_IN_INSIGHTFINDER
        licenseKey = args.LICENSE_KEY
        samplingInterval = args.SAMPLING_INTERVAL_MINUTE
        reportingInterval = args.REPORTING_INTERVAL_MINUTE
        agentType = args.AGENT_TYPE
        return projectName, user, userInsightfinder, licenseKey, samplingInterval, reportingInterval, agentType

    def removeFile(self, filename):
        proc = subprocess.Popen("rm " + filename + "*", cwd=homepath, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                shell=True)
        (out, err) = proc.communicate()

    def clearDownloads(self):
        downloadFiles = ["Attributes.py", "installInsightAgent.py", "startcron.py", "checkpackages.py", "stopcron.py", "get-pip.py"]
        for eachFile in downloadFiles:
            self.removeFile(eachFile)

    def downloadFile(self, filename):
        proc = subprocess.Popen(
            "wget --no-check-certificate https://raw.githubusercontent.com/insightfinder/InsightAgent/cleanup/deployment/" + filename,
            cwd=homepath, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        if "failed" in str(err) or "ERROR" in str(err):
            sys.exit(err)
        os.chmod(filename, 0755)

    def downloadRequiredFiles(self):
        downloadFiles = ["Attributes.py", "installInsightAgent.py", "startcron.py", "checkpackages.py", "stopcron.py", "get-pip.py"]
        for eachFile in downloadFiles:
            self.downloadFile(eachFile)

if __name__ == '__main__':
    homepath = os.getcwd()
    deploy = deployInsightAgent()
    projectName, user, userInsightfinder, licenseKey, samplingInterval, reportingInterval, agentType = deploy.get_args()
    retryOptionAttempts = 3
    retryKeyAttempts = 3
    while retryOptionAttempts:
        passOrKey = raw_input("Enter one of the option:\n[p] for password authentiication\n[k] for key based authentication\n")
        if passOrKey == 'p':
            password=getpass.getpass("Enter %s's password for the deploying hosts:"%user)
            break
        elif passOrKey == 'k':
            password = raw_input("Enter name of identify file with path:")
            while os.path.isfile(password) == False and retryKeyAttempts != 0:
                retryKeyAttempts-=1
                password = raw_input("Invalid file/filepath. Please Enter again:")
            break
        else:
            retryOptionAttempts-=1
            continue
    if retryOptionAttempts == 0 or retryKeyAttempts == 0:
        print "Retry attempts exceeded. Exiting now"
        sys.exit()

    deploy.clearDownloads()
    deploy.downloadRequiredFiles()
    from Attributes import Attributes
    from installInsightAgent import installInsightAgent
    from startcron import startcron
    from checkpackages import checkpackages
    from stopcron import stopcron
    attr = Attributes(projectName, user, userInsightfinder, licenseKey, samplingInterval, reportingInterval, agentType, password)
    attr.displayAttributes()
    checkReq = checkpackages()
    checkReq.installPackagesForDeployment()
    stopagent = stopcron(attr)
    stopagent.stopAgent(stopagent.sshStopCron)
    install = installInsightAgent(attr)
    install.installAgent(install.sshInstall)
    startagent = startcron(attr)
    startagent.deployAgent(startagent.sshDeploy)