#!/bin/bash

function usage()
{
	echo "Usage: ./install.sh -i PROJECT_NAME -u USER_NAME -k LICENSE_KEY -s SAMPLING_INTERVAL_MINUTE -r REPORTING_INTERVAL_MINUTE -t AGENT_TYPE
AGENT_TYPE = proc or cadvisor or docker_remote_api or cgroup or replay or daemonset or hypervisor"
}

if [ "$#" -lt 12 ]; then
	usage
	exit 1
fi

while [ "$1" != "" ]; do
	case $1 in
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

if [ $AGENT_TYPE != 'proc' ] && [ $AGENT_TYPE != 'cadvisor' ] && [ $AGENT_TYPE != 'docker_remote_api' ] && [ $AGENT_TYPE != 'cgroup' ] && [ $AGENT_TYPE != 'replay' ] && [ $AGENT_TYPE != 'daemonset' ] && [ $AGENT_TYPE != 'hypervisor' ]; then
	usage
	exit 1
fi

if [ -z "$INSIGHTAGENTDIR" ]; then
	export INSIGHTAGENTDIR=`pwd`
fi

if [[ ! -d $INSIGHTAGENTDIR/data ]]
then
	rm -rf $INSIGHTAGENTDIR/$AGENT_TYPE/data
fi
mkdir $INSIGHTAGENTDIR/$AGENT_TYPE/data
if [[ -d $INSIGHTAGENTDIR/$AGENT_TYPE/log ]]
then
	rm -rf $INSIGHTAGENTDIR/$AGENT_TYPE/log
fi
mkdir $INSIGHTAGENTDIR/$AGENT_TYPE/log

if [ $AGENT_TYPE == 'daemonset' ]; then
	python $INSIGHTAGENTDIR/common/config/initconfig.py -r $REPORTING_INTERVAL
else
	$INSIGHTAGENTDIR/pyenv/bin/python $INSIGHTAGENTDIR/common/config/initconfig.py -r $REPORTING_INTERVAL -t $AGENT_TYPE
fi

AGENTRC=$INSIGHTAGENTDIR/$AGENT_TYPE/.agent.bashrc
if [[ -f $AGENTRC ]]
then
	rm $AGENTRC
fi
echo "export INSIGHTFINDER_LICENSE_KEY=$LICENSEKEY" >> $AGENTRC
echo "export INSIGHTFINDER_PROJECT_NAME=$PROJECTNAME" >> $AGENTRC
echo "export INSIGHTFINDER_USER_NAME=$USERNAME" >> $AGENTRC
echo "export INSIGHTAGENTDIR=$INSIGHTAGENTDIR" >> $AGENTRC
echo "export SAMPLING_INTERVAL=$SAMPLING_INTERVAL" >> $AGENTRC
echo "export REPORTING_INTERVAL=$REPORTING_INTERVAL" >> $AGENTRC

if [ $AGENT_TYPE == 'replay' ]; then
	exit 1
fi

TEMPCRON=$INSIGHTAGENTDIR/ifagent$AGENT_TYPE
if [[ -f $TEMPCRON ]]
then
	rm $TEMPCRON
fi
USER=`whoami`

if [ $AGENT_TYPE == 'daemonset' ]; then
	echo "*/$SAMPLING_INTERVAL * * * * root python $INSIGHTAGENTDIR/$AGENT_TYPE/getmetrics_$AGENT_TYPE.py -d $INSIGHTAGENTDIR 2>$INSIGHTAGENTDIR/$AGENT_TYPE/log/sampling.err 1>$INSIGHTAGENTDIR/$AGENT_TYPE/log/sampling.out" >> $TEMPCRON
	echo "*/$REPORTING_INTERVAL * * * * root python $INSIGHTAGENTDIR/common/reportMetrics.py -d $INSIGHTAGENTDIR -t $AGENT_TYPE 2>$INSIGHTAGENTDIR/$AGENT_TYPE/log/reporting.err 1>$INSIGHTAGENTDIR/$AGENT_TYPE/log/reporting.out" >> $TEMPCRON
else
	echo "*/$SAMPLING_INTERVAL * * * * root $INSIGHTAGENTDIR/pyenv/bin/python $INSIGHTAGENTDIR/$AGENT_TYPE/getmetrics_$AGENT_TYPE.py -d $INSIGHTAGENTDIR 2>$INSIGHTAGENTDIR/$AGENT_TYPE/log/sampling.err 1>$INSIGHTAGENTDIR/$AGENT_TYPE/log/sampling.out" >> $TEMPCRON
	echo "*/$REPORTING_INTERVAL * * * * root $INSIGHTAGENTDIR/pyenv/bin/python $INSIGHTAGENTDIR/common/reportMetrics.py -d $INSIGHTAGENTDIR -t $AGENT_TYPE 2>$INSIGHTAGENTDIR/$AGENT_TYPE/log/reporting.err 1>$INSIGHTAGENTDIR/$AGENT_TYPE/log/reporting.out" >> $TEMPCRON
fi

sudo chown root:root $TEMPCRON
sudo chmod 644 $TEMPCRON
sudo mv $TEMPCRON /etc/cron.d/

echo "Agent configuration completed. Two cron jobs are created via /etc/cron.d/ifagent"$AGENT_TYPE
