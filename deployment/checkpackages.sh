#!/bin/sh
wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py --force-reinstall --user
wget --no-check-certificate https://raw.githubusercontent.com/insightfinder/InsightAgent/master/deployment/requirements
pip install -U --force-reinstall --user virtualenv
version=`python -c 'import sys; print(str(sys.version_info[0])+"."+str(sys.version_info[1]))'`
python  /home/$USER/.local/lib/python$version/site-packages/virtualenv.py pyenv
source pyenv/bin/activate
pip install -r requirements
deactivate
