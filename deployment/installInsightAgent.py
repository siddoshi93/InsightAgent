#!/usr/bin/python

import sys
import os
import paramiko
import socket
import Queue
import threading

class installInsightAgent:
    def __init__(self, params):
        self.user = params.user;
        self.insightUser = params.insightUser;
        self.licenseKey = params.licenseKey
        self.samplingInterval = params.samplingInterval
        self.reportingInterval = params.reportingInterval
        self.agentType = params.agentType
        self.password = params.password

    def sshInstall(self, retry, hostname, hostQueue):
        if retry == 0:
            print "Install Fail in", hostname
            hostQueue.task_done()
            return
        print "Start installing agent in", hostname, "..."
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
            session.exec_command("sudo rm -rf insightagent* InsightAgent*\n \
            wget --no-check-certificate https://github.com/insightfinder/InsightAgent/archive/cleanup.tar.gz -O insightagent.tar.gz\n \
            tar xzvf insightagent.tar.gz\n \
            cd InsightAgent-cleanup && python deployment/checkpackages.py\n")
            stdin = session.makefile('wb', -1)
            stdout = session.makefile('rb', -1)
            stdin.write(self.password + '\n')
            stdin.flush()
            result = session.recv_exit_status()  # wait for exec_command to finish
            s.close()
            if result != 0:
                return self.sshInstall(retry - 1, hostname)
            print "Install Succeed in", hostname
            hostQueue.task_done()
            return
        except paramiko.SSHException, e:
            print "Invalid Username/Password for %s:" % hostname, e
            return self.sshInstall(retry - 1, hostname, hostQueue)
        except paramiko.AuthenticationException:
            print "Authentication failed for some reason in %s:" % hostname
            return self.sshInstall(retry - 1, hostname, hostQueue)
        except socket.error, e:
            print "Socket connection failed in %s:" % hostname, e
            return self.sshInstall(retry - 1, hostname, hostQueue)
        except:
            print "Unexpected error in %s:" % hostname

    def installAgent(self, sshFunc):
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

    def displayAttributes(self):
        print "InsightFinder username: ", self.insightUser
        print "Host username: ", self.user
        print "Project license key: ", self.licenseKey
        print "Sampling Interval: ", self.samplingInterval
        print "Reporting Interval: ", self.reporintInterval
        print "Agent Type: ", self.agentType
        print "Password: ", self.password


