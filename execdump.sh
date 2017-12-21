#!/bin/bash

#check nic state
ary=($(iwconfig wlan0 | grep Mode))
MODE=3
if [ ${ary[$MODE]} != "Mode:Monitor" ] 
then
    echo turning wlan0 monitor mode...
    nexutil -m2
fi

iface=${1:-wlan0}
scrpref="dump"
filepref="test"
scrname=$scrpref$(date "+%s")

trap 'nexutil -m0; sudo screen -X -S ${scrname} quit; sudo ifdown wlan0; sudo ifup wlan0;' EXIT
sudo screen -d -m -S $scrname airodump-ng -w $filepref -o csv --write-interval 5 $iface
sleep 10
filename=$(ls -t $filepref* | head -1)
echo $filename

python sendtodb.py $filename ${2:-raspberry} 5

