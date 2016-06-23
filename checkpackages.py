#!/bin/python
import os
import sys
import subprocess
required_packages = ["requests","paramiko"]

'''
This script checks for required packages and installs using pip
'''

try:
    import pip
except ImportError as e:
    #Install pip if not found
    homepath = os.getcwd()
    proc = subprocess.Popen(["sudo python "+os.path.join(homepath,"get-pip.py")], cwd=homepath, stdout=subprocess.PIPE, shell=True)
    (out,err) = proc.communicate()
    try:
	import pip
    except ImportError as e:
	print "Dependencies are missing. Please install the dependencies as stated in README"
	sys.exit()
