#!/usr/bin/python

import sys
import os
import argparse
import paramiko
import socket
import Queue
import threading
import json
import subprocess

homepath = os.getenv("INSIGHTAGENTDIR")

if homepath is None:
    homepath = os.getcwd()

deltaFields = ["CPU#%", "DiskRead#MB", "DiskWrite#MB", "NetworkIn#MB", "NetworkOut#MB"]
procFields = ["CPU#%", "DiskRead#MB", "DiskWrite#MB", "DiskUsed#MB", "NetworkIn#MB", "NetworkOut#MB", "MemUsed#MB"]
cadvisorFields = ["CPU#%"]
cgroupFields = ["CPU#%", "DiskRead#MB", "DiskWrite#MB", "NetworkIn#MB", "NetworkOut#MB", "MemUsed#MB"]
dockerRemoteApiFields = ["CPU#%", "DiskRead#MB", "DiskWrite#MB", "NetworkIn#MB", "NetworkOut#MB", "MemUsed#MB"]


def get_args():
    parser = argparse.ArgumentParser(
        description='Script retrieves arguments for insightfinder agent.')
    parser.add_argument(
        '-n', '--USER_NAME_IN_HOST', type=str, help='User Name in Hosts', required=True)
    parser.add_argument(
        '-p', '--PASSWORD', type=str, help='Password for hosts', required=True)
    parser.add_argument(
        '-t', '--AGENTTYPE', type=str, help='Agent type', required=False)
    args = parser.parse_args()
    user = args.USER_NAME_IN_HOST
    password = args.PASSWORD
    agentType = args.AGENTTYPE
    return user, password, agentType


class changeConfig:
    def __init__(self, params):
        self.user = params.user
        self.password = params.password
        self.agentType = params.agentType
        self.datadir = self.agentType + "/data/"

    def getFields(self):
        if self.agentType == "proc":
            fields = procFields
        elif self.agentType == "cadvisor":
            fields = cadvisorFields
        elif self.agentType == "cgroup":
            fields = cgroupFields
        elif self.agentType == "docker_remote_api":
            fields = dockerRemoteApiFields
        else:
            fields = ""
        return fields

    def finalizeConfig(self):
        fields = self.getFields()
        configRetries = 3
        configFields = []
        while configRetries != 0:
            configOption = raw_input("Menu for configuring reporting metrics:\n\
    Enter one of the option:\n[1] To use default metrics\n[2] To edit metrics to be reported\n")
            if configOption == "1":
                return False
            elif configOption == "2":
                print "Selected Option 2"
                for eachfield in fields:
                    print eachfield
                    if (raw_input(
                            "Enter 1 if above field needs to be reported. If no need enter anything else\n") == "1"):
                        configFields.append(eachfield)
                reportingConfig = {'reportingFields': configFields}
                with open(os.path.join(homepath, "config.json"), "w") as conf:
                    json.dump(reportingConfig, conf)
            else:
                print "Wrong Option. Enter Again"
                configRetries -= 1
                continue
            print configFields
            return True
        return False

    def sshConfig(self, retry, hostname, hostQueue):
        if retry == 0:
            print "Config Fail in", hostname
            hostQueue.task_done()
            return
        print "Start Configuring agent in", hostname, "..."
        try:
            s = paramiko.SSHClient()
            s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if os.path.isfile(self.password) == True:
                s.connect(hostname, username=self.user, key_filename=self.password, timeout=60)
            else:
                s.connect(hostname, username=self.user, password=self.password, timeout=60)
            transport = s.get_transport()
            session = transport.open_session()
            session.set_combine_stderr(True)
            session.get_pty()
            configfile = open("config.json", "r")
            line = configfile.readline()
            line = json.dumps(line)
            command = "cd InsightAgent-cleanup\nsudo chown " + self.user + " " + self.agentType + "/data\nsudo echo " + line + " > ./config.json\n"
            print command
            session.exec_command(command)
            stdin = session.makefile('wb', -1)
            stdout = session.makefile('rb', -1)
            stdin.write(self.password + '\n')
            stdin.flush()
            session.recv_exit_status()  # wait for exec_command to finish
            s.close()
            print "Config Succeed in", hostname
            hostQueue.task_done()
            return
        except paramiko.SSHException, e:
            print "Invalid Username/Password for %s:" % hostname, e
            return self.sshConfig(retry - 1, hostname)
        except paramiko.AuthenticationException:
            print "Authentication failed for some reason in %s:" % hostname
            return self.sshConfig(retry - 1, hostname)
        except socket.error, e:
            print "Socket connection failed in %s:" % hostname, e
            return self.sshConfig(retry - 1, hostname)
        except:
            print "Unexpected error in %s:" % hostname
            sys.exit()

    def configChange(self, sshFunc):
        hostfile = "hostlist.txt"
        q = Queue.Queue()
        try:
            with open(os.getcwd() + "/" + hostfile, 'rb') as f:
                while True:
                    line = f.readline()
                    if line:
                        host = line.split("\n")[0]
                        q.put(host)
                    else:
                        break
                while q.empty() != True:
                    host = q.get()
                    t = threading.Thread(target=sshFunc, args=(3, host, q))
                    t.daemon = True
                    t.start()
                q.join()
        except (KeyboardInterrupt, SystemExit):
            print "Keyboard Interrupt!!"
            sys.exit()
        except IOError as e:
            print "I/O error({0}): {1}: {2}".format(e.errno, e.strerror, e.filename)
            sys.exit()

if __name__ == '__main__':
    global user
    global password
    global agentType
    global hostfile
    user, password, agentType = get_args()
    if os.path.isfile("Attributes.py") == False:
        proc = subprocess.Popen("wget --no-check-certificate https://raw.githubusercontent.com/insightfinder/InsightAgent/cleanup/deployment/Attributes.py",
            cwd=homepath, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        if "failed" in str(err) or "ERROR" in str(err):
            sys.exit(err)
    from Attributes import Attributes
    attr = Attributes(user=user, password=password, agentType=agentType)
    attr.displayAttributes()
    config = changeConfig(attr)
    if config.finalizeConfig() == True:
        config.configChange(config.sshConfig)
    os.remove("changeConfig.py")
    os.remove("Attributes.py")

