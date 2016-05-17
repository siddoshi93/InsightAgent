#!/usr/bin/python

import argparse
import getpass
import subprocess
import os
import sys

'''
This script will start two scripts for deploying insightagent to hosts
'''

def get_args():
    parser = argparse.ArgumentParser(description='Script retrieves arguments for insightfinder agent.')
    parser.add_argument('-n', '--USER_NAME_IN_HOST', type=str, help='User Name in Hosts', required=True)
    parser.add_argument('-u', '--USER_NAME_IN_INSIGHTFINDER', type=str, help='User Name in Insightfinder', required=True)
    parser.add_argument('-k', '--LICENSE_KEY', type=str, help='License key of an agent project', required=True)
    parser.add_argument('-s', '--SAMPLING_INTERVAL_MINUTE', type=str, help='Sampling Interval Minutes', required=True)
    parser.add_argument('-r', '--REPORTING_INTERVAL_MINUTE', type=str, help='Reporting Interval Minutes', required=True)
    parser.add_argument('-t', '--AGENT_TYPE', type=str, help='Agent type: proc or docker', choices=['proc', 'docker'],required=True)
    args = parser.parse_args()
    user = args.USER_NAME_IN_HOST
    user_insightfinder = args.USER_NAME_IN_INSIGHTFINDER
    license_key = args.LICENSE_KEY
    sampling_interval = args.SAMPLING_INTERVAL_MINUTE
    reporting_interval = args.REPORTING_INTERVAL_MINUTE
    agent_type = args.AGENT_TYPE
    return user, user_insightfinder, license_key, sampling_interval, reporting_interval, agent_type


if __name__ == '__main__':
    global user
    global host
    global password
    global hostfile
    global user_insightfinder
    global license_key
    global sampling_interval
    global reporting_interval
    global agent_type

    homepath = os.getcwd()
    proc = subprocess.Popen("wget --no-check-certificate https://raw.githubusercontent.com/insightfinder/InsightAgent/testing/installInsightAgent.py", cwd=homepath, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out,err) = proc.communicate()
    if "failed" in str(err) or "ERROR" in str(err):
        sys.exit(err)
    proc = subprocess.Popen("wget --no-check-certificate https://raw.githubusercontent.com/insightfinder/InsightAgent/testing/startcron.py", cwd=homepath, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out,err) = proc.communicate()
    if "failed" in str(err) or "ERROR" in str(err):
        sys.exit(err)
    proc = subprocess.Popen("wget --no-check-certificate https://raw.githubusercontent.com/insightfinder/InsightAgent/testing/checkpackages.py", cwd=homepath, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out,err) = proc.communicate()
    if "failed" in str(err) or "ERROR" in str(err):
        sys.exit(err)
    proc = subprocess.Popen("wget --no-check-certificate https://raw.githubusercontent.com/insightfinder/InsightAgent/testing/get-pip.py", cwd=homepath, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out,err) = proc.communicate()
    if "failed" in str(err) or "ERROR" in str(err):
        sys.exit(err)
    os.chmod("installInsightAgent.py",0755)
    os.chmod("startcron.py",0755)
    os.chmod("checkpackages.py",0755)
    os.chmod("get-pip.py",0755)

    #Check if required packages are installed
    proc = subprocess.Popen(["sudo python "+os.path.join(homepath,"checkpackages.py")], cwd=homepath, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out,err) = proc.communicate()
    if "failed" in str(err) or "ERROR" in str(err):
        sys.exit(err)

    user, user_insightfinder, license_key, sampling_interval, reporting_interval, agent_type = get_args()
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
    stat=True
    print "Starting Installation"
    proc = subprocess.Popen([os.path.join(homepath,"installInsightAgent.py")+" -n "+user+" -u "+user_insightfinder+" -k "+license_key+" -s "+sampling_interval+" -r "+reporting_interval+" -p "+password], cwd=homepath, stdout=subprocess.PIPE, shell=True)
    (out,err) = proc.communicate()
    if "error" in out:
        sys.exit(out)
    print out
    print "Proceeding to Deployment"
    proc = subprocess.Popen([os.path.join(homepath,"startcron.py")+" -n "+user+" -u "+user_insightfinder+" -k "+license_key+" -s "+sampling_interval+" -r "+reporting_interval+" -t "+agent_type+" -p "+password], cwd=homepath, stdout=subprocess.PIPE, shell=True)
    (out,err) = proc.communicate()
    print out
