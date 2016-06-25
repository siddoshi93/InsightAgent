# InsightAgent

###### Pre-requisites:
Minimum required docker version for monitoring docker containers: v1.7.x

This pre-requisite is needed on the machine which launches deployInsightAgent.py.
For Debian and Ubuntu, the following command will ensure that the required dependencies are installed:

sudo apt-get install build-essential libssl-dev libffi-dev python-dev

For Fedora and RHEL-derivatives, the following command will ensure that the required dependencies are installed:

sudo yum install gcc libffi-devel python-devel openssl-devel

For AGENT_TYPE = cadvisor, cAdvisor should be running in all hosts.
- To run cAdvisor use
```
sudo docker run \
  --cpuset=3 \
  --volume=/:/rootfs:ro \
  --volume=/var/run:/var/run:rw \
  --volume=/sys:/sys:ro \
  --volume=/var/lib/docker/:/var/lib/docker:ro \
  --publish=8080:8080 \
  --detach=true \
  --name=cadvisor \
  google/cadvisor:latest
```

###### To deploy agent on multiple hosts:

- Get the deployment script from github using below command:
```
wget --no-check-certificate https://raw.githubusercontent.com/insightfinder/InsightAgent/staging/deployInsightAgent.py
```
- Include IP address of all hosts in hostlist.txt and enter one IP address per line.
- To deploy run the following command:
```
python deployInsightAgent.py -n USER_NAME_IN_HOST
                             -u USER_NAME_IN_INSIGHTFINDER 
                             -k LICENSE_KEY 
                             -s SAMPLING_INTERVAL_MINUTE 
                             -r REPORTING_INTERVAL_MINUTE 
                             -t AGENT_TYPE
```
Currently, AGENT_TYPE can be *proc* or *cadvisor* or *docker_remote_api*.

When the above script is run, if prompted for password, enter either the password or the name of the identity file along with file path.
Example: /home/insight/.ssh/id_rsa


###### To get more details on the command, run 
```
python deployInsightAgent.py -h
```

###### To undo agent deployment on multiple hosts:
- Get the script for stopping agents from github using below command:
```
wget --no-check-certificate https://raw.githubusercontent.com/insightfinder/InsightAgent/staging/stopcron.py
```

- Include IP address of all hosts in hostlist.txt and enter one IP address per line.

- To stop the agent run the following command:
```
python stopcron.py -n USER_NAME_IN_HOST -p PASSWORD
```

###### To install agent on local machine:
```
./install.sh -u USER_NAME -k LICENSE_KEY -s SAMPLING_INTERVAL_MINUTE -r REPORTING_INTERVAL_MINUTE -t AGENT_TYPE
```


