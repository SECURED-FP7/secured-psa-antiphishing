#!/bin/bash
#
# start.sh
#   Created:    19/09/2016
#   Author:     Diego Montero
#
#   Description:
#       Sleep a time then reconfigure squid to load the updated antiphishin url list


##############################################################
#sleep some time then reconfigure squid
#echo "SLEEPING 4s then reconfigure"
#sleep 4s
#squid3 -k reconfigure -f /home/psa/pythonScript/antiphishingSquidConfiguration
#squid3 -k reconfigure

echo "SLEEPING 2m then reconfigure"
sleep 2m
/usr/sbin/squid3 -k reconfigure

exit 1;
