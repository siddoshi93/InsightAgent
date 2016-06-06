#!/bin/sh
DATADIR='data/'
cd ../$DATADIR
echo $1
while [ "$1" != "" ]; do
	SEARCHKEY=$1
	shift
done
echo $SEARCHKEY

for SEARCHKEY in "rubis_apache" "rubis_db"
do
echo $SEARCHKEY
apacheweb=$(sudo docker ps --no-trunc | grep $SEARCHKEY | awk '{print $1}')
echo $apacheweb
CONTAINER_PID=`sudo docker inspect -f '{{ .State.Pid }}' $apacheweb`
date +%s%3N | awk '{print "timestamp="$1}' > timestamp.txt & PID1=$!
sudo cat /cgroup/memory/docker/$apacheweb/memory.usage_in_bytes | awk '{print "MemUsed="$1}' > memmetrics_$SEARCHKEY.txt & PID2=$!

sudo cat /cgroup/blkio/docker/$apacheweb/blkio.throttle.io_service_bytes | grep Read | awk '{if(NR!=1){readbytes+=$3}} END{print "DiskRead="readbytes}' > diskmetricsread_$SEARCHKEY.txt & PID3=$!
sudo cat /cgroup/blkio/docker/$apacheweb/blkio.throttle.io_service_bytes | grep Write | awk '{if(NR!=1){writebytes+=$3;}} END{print "DiskWrite="writebytes}' > diskmetricswrite_$SEARCHKEY.txt & PID4=$!
sudo cat /proc/$CONTAINER_PID/net/dev | awk '{if(NR!=1 && NR!=2){if($1!="lo:"){rxbytes+=$2;txbytes+=$10;}}} END{print "NetworkIn="rxbytes; print "NetworkOut="txbytes}' > networkmetrics_$SEARCHKEY.txt & PID5=$!

wait $PID1
wait $PID2
wait $PID3
wait $PID4
wait $PID5
done
