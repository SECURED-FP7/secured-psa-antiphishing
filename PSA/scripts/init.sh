#!/bin/bash
#
# init.sh
#   Created:    18/06/2015
#   Author:     Diego Montero
#
#   Description:
#       Init script which setups the environment for squid to run as a
#       transparent proxy.
#

# 
# This script is called by the PSA API when the PSA's is initialized and psaconf file is saved to psaConfigs/ folder. 
# This script should do what is required with that configuration and peform any other initialization tasks. 
# After this has been executed the PSA should be startable by calling START (start.sh).
# 
# Return value: 
# 1: init ok
# 0: init not ok
#

# SQUID TRANSPARENT PROXY (TPROXY)
# 
#    10.2.2.1                       br0:10.2.2.10      GW: 10.2.2.254
#  +-----------+         +-----+       +-------+         +-----+           +-------------+
#  | End User  |---------| NED |-------| Squid |---------| NAT |-----------| http server |
#  +-----------+         +-----+       +-------+         +-----+           +-------------+
#                                    eth0     eth1     eth0    eth1(public IP)
# 
#                 NET1               Bridge br0      NET1   |        Internet        
# 
# Requirement: br0 has to be configured with an IP address whitin NET1 space
# Example: NET1 = 10.2.2.0/24
# INET_IPv4_ADDRESS='10.2.2.10/24'

# ########
# stop squid
service squid3 stop

# SQUID TPROXY
echo "loading modules requierd for the tproxy"
modprobe ip_tables
modprobe xt_tcpudp
#modprobe nf_tproxy_core
modprobe xt_mark
#modprobe xt_MARK
modprobe xt_TPROXY
modprobe xt_socket
modprobe nf_conntrack_ipv4
sysctl net.netfilter.nf_conntrack_acct
sysctl net.netfilter.nf_conntrack_acct=1
sysctl -w net.ipv4.ip_forward=1

# Hack for the SSL credentials -- squid tproxy
rm -rf /var/lib/ssl_db
/usr/lib/squid3/ssl_crtd -c -s /var/lib/ssl_db
chown -R proxy:proxy /var/lib/ssl_db 

echo "setting routing tables for tproxy"
ip route flush table 100
ip rule del fwmark 1 lookup 100
ip rule add fwmark 1 lookup 100
ip -f inet route add local default dev lo table 100

echo "flushing any exiting rules"
iptables -t mangle -F
iptables -t mangle -X DIVERT

echo "creating iptables rules"
iptables -t mangle -N DIVERT
iptables -t mangle -A DIVERT -j MARK --set-mark 1
iptables -t mangle -A DIVERT -j ACCEPT
iptables -t mangle -A PREROUTING -p tcp -m socket -j DIVERT
iptables -t mangle -A PREROUTING -i eth0 -p tcp -m tcp --dport 80 -j TPROXY --on-port 3128 --tproxy-mark 0x1/0x1
iptables -t mangle -A PREROUTING -i eth0 -p tcp -m tcp --dport 443 -j TPROXY --on-port 3129 --tproxy-mark 0x1/0x1

echo "flushing routing cache"
ip route flush cache

## interface facing clients
CLIENT_IFACE=eth0

## interface facing Internet
INET_IFACE=eth1

##LastPSA
psaparams="/home/psa/pythonScript/psaConfigs/psaparams.json"
if [ -f $psaparams ]
then
 mobility=($(jq '.mobility' $psaparams))
 if [ "${mobility,,}" = "null" ]; then mobility=false;fi
 firstPSA=($(jq '.firsPSA' $psaparams))
 if [ "${firstPSA,,}" = "null" ]; then firstPSA=false;fi
 lastPSA=($(jq '.lastPSA' $psaparams))
 if [ "${lastPSA,,}" = "null" ]; then lastPSA=false;fi
fi


ebtables -P FORWARD DROP
ebtables -A FORWARD -p IPv4 -j ACCEPT
ebtables -A FORWARD -p ARP -j ACCEPT

if [ "${mobility,,}" = "false" ] || ([ "${mobility,,}" = "true" ] && [ "${lastPSA,,}" = "false" ])
 then
  ebtables -t broute -A BROUTING -i $CLIENT_IFACE -p ipv4 --ip-proto tcp --ip-dport 80 -j redirect --redirect-target DROP
  ebtables -t broute -A BROUTING -i $INET_IFACE -p ipv4 --ip-proto tcp --ip-sport 80 -j redirect --redirect-target DROP
  ebtables -t broute -A BROUTING -i $CLIENT_IFACE -p ipv4 --ip-proto tcp --ip-dport 443 -j redirect --redirect-target DROP
  ebtables -t broute -A BROUTING -i $INET_IFACE -p ipv4 --ip-proto tcp --ip-sport 443 -j redirect --redirect-target DROP
else
 ebtables -t broute -A BROUTING -i $CLIENT_IFACE -p ipv4 -j redirect --redirect-target DROP
 ebtables -t broute -A BROUTING -i $INET_IFACE -p ipv4 -j redirect --redirect-target DROP
 iptables -t nat -A POSTROUTING -o br0 -j MASQUERADE
fi

for i in /proc/sys/net/bridge/*
do
  echo 0 > $i
done
unset i

### Update the antiphishin url list
echo "Updating phishing list..."
python /home/psa/pythonScript/updateListSource/antiphishingListUpdate.py &

exit 1;
