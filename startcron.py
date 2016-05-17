#!/usr/bin/python

import sys
import time
import os
import getpass
import getopt
import argparse
import re
import paramiko
import socket
import Queue
import threading

def sshDeploy(retry,hostname):
    global user
    global password
    global user_insightfinder
    global license_key
    global sampling_interval
    global reporting_interval
    global agent_type
    global expectations
    if retry == 0:
        print "Deploy Fail in", hostname
        q.task_done()
        return
    print "Start deploying agent in", hostname, "..."
    try:
        s = paramiko.SSHClient()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if os.path.isfile(password) == True:
            s.connect(host, username=user, key_filename = password, timeout=60)
        else:
            s.connect(host, username=user, password = password, timeout=60)
        transport = s.get_transport()
        session = transport.open_session()
        session.set_combine_stderr(True)
        session.get_pty()
        command="cd InsightAgent-testing && sudo ./install.sh -u "+user_insightfinder+" -k "+license_key+" -s "+sampling_interval+" -r "+reporting_interval+" -t "+agent_type
        session.exec_command(command)
        stdin = session.makefile('wb', -1)
        stdout = session.makefile('rb', -1)
        stdin.write(password+'\n')
        stdin.flush()
        session.recv_exit_status() #wait for exec_command to finish
        s.close()
        print "Deploy Succeed in", hostname
        q.task_done()
        return
    except paramiko.SSHException, e:
        print "Invalid Username/Password for %s:"%hostname , e
        return sshDeploy(retry-1,hostname)
    except paramiko.AuthenticationException:
        print "Authentication failed for some reason in %s"%hostname
        return sshDeploy(retry-1,hostname)
    except socket.error, e:
        print "Socket connection failed in %s:"%hostname, e
        return sshDeploy(retry-1,hostname)

def get_args():
    parser = argparse.ArgumentParser(
        description='Script retrieves arguments for insightfinder agent.')
    parser.add_argument(
        '-n', '--USER_NAME_IN_HOST', type=str, help='User Name in Hosts', required=True)
    parser.add_argument(
        '-u', '--USER_NAME_IN_INSIGHTFINDER', type=str, help='User Name in Insightfinder', required=True)
    parser.add_argument(
        '-k', '--LICENSE_KEY', type=str, help='License key of an agent project', required=True)
    parser.add_argument(
        '-s', '--SAMPLING_INTERVAL_MINUTE', type=str, help='Sampling Interval Minutes', required=True)
    parser.add_argument(
        '-r', '--REPORTING_INTERVAL_MINUTE', type=str, help='Reporting Interval Minutes', required=True)
    parser.add_argument(
        '-t', '--AGENT_TYPE', type=str, help='Agent type: proc or docker', choices=['proc', 'docker'], required=True)
    parser.add_argument(
        '-p', '--PASSWORD', type=str, help='Password for hosts', required=True)
    args = parser.parse_args()
    user = args.USER_NAME_IN_HOST
    user_insightfinder = args.USER_NAME_IN_INSIGHTFINDER
    license_key = args.LICENSE_KEY
    sampling_interval = args.SAMPLING_INTERVAL_MINUTE
    reporting_interval = args.REPORTING_INTERVAL_MINUTE
    agent_type = args.AGENT_TYPE
    password = args.PASSWORD
    return user, user_insightfinder, license_key, sampling_interval, reporting_interval, agent_type, password


if __name__ == '__main__':
    global user
    global password
    global hostfile
    global user_insightfinder
    global license_key
    global sampling_interval
    global reporting_interval
    global agent_type
    hostfile="hostlist.txt"
    user, user_insightfinder, license_key, sampling_interval, reporting_interval, agent_type, password = get_args()
    q = Queue.Queue()
    try:
        with open(os.getcwd()+"/"+hostfile, 'rb') as f:
            while True:
                line = f.readline()
                if line:
                    host=line.split("\n")[0]
                    q.put(host)
                else:
                    break
            while q.empty() != True:
                host = q.get()
                t = threading.Thread(target=sshDeploy, args=(3,host,))
                t.daemon = True
                t.start()
            q.join()
    except (KeyboardInterrupt, SystemExit):
        print "Keyboard Interrupt!!"
        sys.exit()
    except IOError as e:
        print "I/O error({0}): {1}: {2}".format(e.errno, e.strerror, e.filename)
        sys.exit()
