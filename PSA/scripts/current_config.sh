#!/bin/bash
#
# status.sh
# 
# This script is called by the PSA API when the PSA's current runtime configuration is requested.
# 
# Return value: 
# Current configuration
#

COMMAND_OUTPUT="$(iptables -L)"
echo ${COMMAND_OUTPUT}
exit 1;

