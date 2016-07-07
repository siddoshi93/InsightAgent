#!/usr/bin/python

import os
import sys
import paramiko
import socket
import Queue
import threading
import time
from Attributes import Attributes

class stopcron:
    def __init__(self, params):
        self.user = params.user;
        self.password = params.password

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
            command = "sudo mv /etc/cron.d/ifagent InsightAgent-cleanup/ifagent." + time.strftime("%Y%m%d%H%M%S") + "\n"
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
if __name__ == '__main__':
    attr = Attributes("proc", "rchandh", "rchandh", "adsdfs", "1", "1", "proc", "Raknahsivar2590")
    print os.getcwd()
    st = stopcron(attr)
    st.stopAgent(st.sshStopCron)
    st.stopAgent(st.sshRemoveAgent)