#!/bin/bash

function usage()
{
	echo "Usage: ./install.sh -n USER_NAME_IN_HOST -i PROJECT_NAME -u USER_NAME -k LICENSE_KEY -s SAMPLING_INTERVAL_MINUTE -r REPORTING_INTERVAL_MINUTE -t AGENT_TYPE
AGENT_TYPE = proc or cadvisor or docker_remote_api or cgroup or filereplay or daemonset or hypervisor"
}

if [ "$#" -lt 14 ]; then
	usage
	exit 1
fi

while [ "$1" != "" ]; do
	case $1 in
		-n )	shift
			INSIGHTFINDER_USERNAME=$1
			;;
		-k )	shift
			LICENSEKEY=$1
			;;
		-i )	shift
			PROJECTNAME=$1
			;;
		-u )	shift
			USERNAME=$1
			;;
		-s )	shift
			SAMPLING_INTERVAL=$1
			;;
		-r )	shift
			REPORTING_INTERVAL=$1
			;;
		-t )	shift
			AGENT_TYPE=$1
			;;
		* )	usage
			exit 1
	esac
	shift
done

if [ $AGENT_TYPE != 'proc' ] && [ $AGENT_TYPE != 'cadvisor' ] && [ $AGENT_TYPE != 'docker_remote_api' ] && [ $AGENT_TYPE != 'cgroup' ] && [ $AGENT_TYPE != 'filereplay' ] && [ $AGENT_TYPE != 'daemonset' ] && [ $AGENT_TYPE != 'hypervisor' ]; then
	usage
	exit 1
fi

wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py --force-reinstall --user
wget --no-check-certificate https://raw.githubusercontent.com/insightfinder/InsightAgent/master/deployment/requirements
pip install -U --force-reinstall --user virtualenv
version=`python -c 'import sys; print(str(sys.version_info[0])+"."+str(sys.version_info[1]))'`
python  /home/$USER/.local/lib/python$version/site-packages/virtualenv.py pyenv
source pyenv/bin/activate
pip install -r requirements
deactivate

rm requirements
rm get-pip.py

wget --no-check-certificate https://raw.githubusercontent.com/insightfinder/InsightAgent/master/deployment/deployInsightAgent.py
sudo python deployInsightAgent.py -n $INSIGHTFINDER_USERNAME -i $PROJECTNAME -u $USERNAME -k $LICENSEKEY -s $SAMPLING_INTERVAL -r $REPORTING_INTERVAL -t $AGENT_TYPE
rm -rf pyenv
rm deployInsightAgent.sh
