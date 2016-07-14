#!/usr/bin/python

import argparse
import os
import sys
import paramiko
import socket
import Queue
import threading
import time
from Attributes import Attributes
import subprocess

BRANCH = "cleanup"

class stopcron:
    def __init__(self, params):
        self.user = params.user;
        self.password = params.password
        self.agentType = params.agentType

    def sshStopCron(self, retry, hostname, hostQueue):
        if retry == 0:
            print "Stop Cron Failed in", hostname
            hostQueue.task_done()
            return
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
            command = "sudo mv /etc/cron.d/ifagent"+self.agentType+" InsightAgent-"+BRANCH+"/"+self.agentType+"/ifagent"+self.agentType+"." + time.strftime("%Y%m%d%H%M%S") + "\n" \
            "sed -i 's#\""+self.agentType+"\": \"1\"#\""+self.agentType+"\": \"0\"#g' InsightAgent-"+BRANCH+"/agentLookup.json\n"
            #"sed - i 's#"replay": "0"#"replay": "1"#g' InsightAgent-"+BRANCH+"agentLookup.json
            print command
            session.exec_command(command)
            stdin = session.makefile('wb', -1)
            stdout = session.makefile('rb', -1)
            stdin.write(self.password + '\n')
            stdin.flush()
            session.recv_exit_status()  # wait for exec_command to finish
            s.close()
            print "Stopped Cron in ", hostname
            hostQueue.task_done()
            return
        except paramiko.SSHException, e:
            print "Invalid Username/Password for %s:" % hostname, e
            return self.sshStopCron(retry - 1, hostname, hostQueue)
        except paramiko.AuthenticationException:
            print "Authentication failed for some reason in %s:" % hostname
            return self.sshStopCron(retry - 1, hostname, hostQueue)
        except socket.error, e:
            print "Socket connection failed in %s:" % hostname, e
            return self.sshStopCron(retry - 1, hostname, hostQueue)

    def stopAgent(self, sshFunc):
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
                    t = threading.Thread(target=sshFunc, args=(3, host,q,))
                    t.daemon = True
                    t.start()
                q.join()
        except (KeyboardInterrupt, SystemExit):
            print "Keyboard Interrupt!!"
            sys.exit()
        except IOError as e:
            print "I/O error({0}): {1}: {2}".format(e.errno, e.strerror, e.filename)
            sys.exit()

    def sshRemoveAgent(self, retry, hostname, hostQueue):
        if retry == 0:
            print "Remove Agent Failed in", hostname
            hostQueue.task_done()
            return
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
            command = "sudo rm -rf insightagent* InsightAgent*\n"
            session.exec_command(command)
            stdin = session.makefile('wb', -1)
            stdout = session.makefile('rb', -1)
            stdin.write(self.password + '\n')
            stdin.flush()
            session.recv_exit_status()  # wait for exec_command to finish
            s.close()
            print "Removed Agent in ", hostname
            hostQueue.task_done()
            return
        except paramiko.SSHException, e:
            print "Invalid Username/Password for %s:" % hostname, e
            return self.sshRemoveAgent(retry - 1, hostname, hostQueue)
        except paramiko.AuthenticationException:
            print "Authentication failed for some reason in %s:" % hostname
            return self.sshRemoveAgent(retry - 1, hostname, hostQueue)
        except socket.error, e:
            print "Socket connection failed in %s:" % hostname, e
            return self.sshRemoveAgent(retry - 1, hostname, hostQueue)

'''
    def removeAgent(self):
        hostfile = "hostlist.txt"

        try:
            with open(os.getcwd() + "/" + hostfile, 'rb') as f:
                while True:
                    line = f.readline()
                    if line:
                        host = line.split("\n")[0]
                        self.q.put(host)
                    else:
                        break
                while self.q.empty() != True:
                    host = self.q.get()
                    t = threading.Thread(target=self.sshRemoveAgent, args=(3, host,))
                    t.daemon = True
                    t.start()
                self.q.join()
        except (KeyboardInterrupt, SystemExit):
            print "Keyboard Interrupt!!"
            sys.exit()
        except IOError as e:
            print "I/O error({0}): {1}: {2}".format(e.errno, e.strerror, e.filename)
            sys.exit()
'''


def get_args():
    parser = argparse.ArgumentParser(description='Script retrieves arguments for insightfinder agent.')
    parser.add_argument('-n', '--USER_NAME_IN_HOST', type=str, help='User Name in Hosts', required=True)
    parser.add_argument('-p', '--PASSWORD', type=str, help='Password for hosts', required=True)
    parser.add_argument('-t', '--AGENT_TYPE', type=str,
                        help='Agent type: proc or cadvisor or docker_remote_api or cgroup or daemonset',
                        choices=['proc', 'cadvisor', 'docker_remote_api', 'cgroup', 'daemonset'], required=True)
    args = parser.parse_args()
    user = args.USER_NAME_IN_HOST
    password = args.PASSWORD
    agentType = args.AGENT_TYPE
    return user, password, agentType


def downloadFile(self, filename):
    proc = subprocess.Popen(
        "wget --no-check-certificate https://raw.githubusercontent.com/insightfinder/InsightAgent/" + BRANCH + "/deployment/" + filename,
        cwd=homepath, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    if "failed" in str(err) or "ERROR" in str(err):
        sys.exit(err)
    os.chmod(filename, 0755)


def removeFile(self, filename):
    proc = subprocess.Popen("rm " + filename + "*", cwd=homepath, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            shell=True)
    (out, err) = proc.communicate()

if __name__ == '__main__':
    user, password, agentType = get_args()
    downloadFile("Attributes.py")
    attr = Attributes(user=user, password=password, agentType=agentType)
    print os.getcwd()
    st = stopcron(attr)
    st.stopAgent(st.sshStopCron)
    removeFile("Attributes.py")
    removeFile("stopcron.py")
