#!/usr/bin/python

import argparse
import getpass
import os
import sys
import paramiko
import socket
import Queue
import threading

def sshStopCron(retry,hostname):
    global user
    global password
    if retry == 0:
        print "Stop Cron Failed in", hostname
        q.task_done()
        return
    try:
        s = paramiko.SSHClient()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if os.path.isfile(password) == True:
            s.connect(hostname, username=user, key_filename = password, timeout=60)
        else:
            s.connect(hostname, username=user, password = password, timeout=60)
        transport = s.get_transport()
        session = transport.open_session()
        session.set_combine_stderr(True)
        session.get_pty()
        session.exec_command("sudo rm /etc/cron.d/ifagent\n")
        stdin = session.makefile('wb', -1)
        stdout = session.makefile('rb', -1)
        stdin.write(password+'\n')
        stdin.flush()
        session.recv_exit_status() #wait for exec_command to finish
        s.close()
        print "Stopped Cron in ", hostname
        q.task_done()
        return
    except paramiko.SSHException, e:
        print "Invalid Username/Password for %s:"%hostname , e
        return sshStopCron(retry-1,hostname)
    except paramiko.AuthenticationException:
        print "Authentication failed for some reason in %s:"%hostname
        return sshStopCron(retry-1,hostname)
    except socket.error, e:
        print "Socket connection failed in %s:"%hostname, e
        return sshStopCron(retry-1,hostname)

def get_args():
    parser = argparse.ArgumentParser(
        description='Script retrieves arguments for stopping insightfinder agent.')
    parser.add_argument(
        '-n', '--USER_NAME_IN_HOST', type=str, help='User Name in Hosts', required=True)
    args = parser.parse_args()
    user = args.USER_NAME_IN_HOST
    return user

if __name__ == '__main__':
    hostfile="hostlist.txt"
    q = Queue.Queue()
    user = get_args()

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
                t = threading.Thread(target=sshStopCron, args=(3,host,))
                t.daemon = True
                t.start()
            q.join()
    except (KeyboardInterrupt, SystemExit):
        print "Keyboard Interrupt!!"
        sys.exit()
    except IOError as e:
        print "I/O error({0}): {1}: {2}".format(e.errno, e.strerror, e.filename)
        sys.exit()
