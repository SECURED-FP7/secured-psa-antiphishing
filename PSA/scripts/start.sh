#!/bin/bash
#
# start.sh
#   Created:    18/06/2015
#   Author:     Diego Montero
#
#   Description:
#       Start script for the PSA-squid
#
# This script is called by the PSA API when the PSA is requested to be started.

# Load PSA's current configuration

##############################################################
#Initializing Squid
service squid3 stop
squid3 -f /home/psa/pythonScript/antiphishingSquidConfiguration

bash /home/psa/pythonScript/scripts/sleep.sh &

echo "PSA Started"

exit 1;

