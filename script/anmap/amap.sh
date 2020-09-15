#!/bin/bash
echo "---------------------------------------------------------------"
echo "usage:./scan.sh [ports]"
echo "      ./scan.sh 1-65535 scan ip in host.txt, ports 1-65535"
echo "      ./scan.sh 3306 scan ip in host.txt, ports 3306"
echo "      ./scan.sh 80,8000-9000,20-22,3306-3310 scan ip in host.txt, ports 80,8000-9000,20-22,3306-3310"
echo "---------------------------------------------------------------"
ports=$1
if [ -n "$ports" ]
then
   echo "ports use input param $ports"
else
   ports="1-65535"
   echo "ports use default $ports"
fi
echo "---------------------------------------------------------------"
echo "scan start at `date +'%Y-%m-%d %H:%M.%S'`"
start=$(date +%s)
workdir=$(cd $(dirname $0); pwd)
result="scan-result-amap-`date +'%Y%m%d-%H'`.txt"

echo "workdir:${workdir}"
echo "result file:$result"

rm $result
touch $result

i=0;
for line in `cat hosts.txt`
do
  if [ -n "$line" ]; then
    ((i++))
    ip=$line
    echo "start scan $i, ip= $ip"
    echo "amap -1 -b -q -t 1 -T 1 -C 0 -c 32 -H $ip $ports |grep 'Protocol\|Unrecognized'"
    amap -1 -b -q -t 1 -T 1 -C 0 -c 32 -H $ip $ports |grep 'Protocol\|Unrecognized' >> $result
  fi
done

end=$(date +%s)
cost=$(( end - start ))
echo "cost total $cost seconds." 
echo "scan end at `date +'%Y-%m-%d %H:%M.%S'`"

echo "-------------------------result info:-------------------------"
cat $result
echo "---------------------------------------------------------------"

