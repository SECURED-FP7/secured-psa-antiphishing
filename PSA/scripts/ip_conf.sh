#!/bin/bash
#
# ip_conf.sh
# 
# This script is called by the PSA API when the PSA should be configured with IP address. 
# NOTE: This script is called right after init.sh script at the start-up of a PSA.
# !!! 
# This should have the base setup for IP. init.sh should not change these values, since it 
# will overwrite these values at the moment.
# !!!
# --> (We can change the logic to call this after init.sh always?)
#

# Please, define the interface this PSA requires the IP for.
CLIENT_IFACE=br0
if [ "$#" -ne 4 ] 
then
    echo "Illegal number of params. Should be 4 (IP, gateway, dns, netmask)"
    exit 1;
fi

echo "-------------"
echo "IP:" + $1
echo "gateway:" + $2
echo "dns:" + $3
echo "netmask:" + $4

# Note that now we just replace any existing conf, since this should be the only DNS for the PSA.
SEARCH='nameserver '$3
if grep -Fxq "$SEARCH" /etc/resolv.conf
then
    echo "Had dns already"
else
    echo "Didn't have dns, setting"
    echo -e "$SEARCH" > /etc/resolv.conf
fi

/sbin/ifconfig $CLIENT_IFACE $1 netmask $4
ip route delete default
/sbin/route add default gw $2 $CLIENT_IFACE

