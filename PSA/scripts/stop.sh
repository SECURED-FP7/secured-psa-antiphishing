#!/bin/bash
#
# stop.sh
#   Created:    18/06/2015
#   Author:     Diego Montero
#   
#   Description:
#       This script stops squid3 and clear the configuration environmet.
# 
# This script is called by the PSA API when the PSA is requested to be stopped.
# 

# We don't need to save current config
#iptables-save > psaConfigs/12345

# Flush iptables
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

iptables -t nat -F

ip route flush table 100
ip rule del fwmark 1 lookup 100

echo "flushing any exiting rules"
iptables -t mangle -F
iptables -t mangle -X DIVERT

echo "flushing routing cache"
ip route flush cache

##########################################################
echo "flusing ebtables"
ebtables -F
ebtables -X
for T in filter nat broute; do   ebtables -t $T -F;   ebtables -t $T -X; done
ebtables -P INPUT ACCEPT
ebtables -P FORWARD ACCEPT
ebtables -P OUTPUT ACCEPT

echo "stopping squid3"
service squid3 stop

echo "PSA Stopped"
exit 1;

