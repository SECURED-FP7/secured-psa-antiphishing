#!/bin/bash
#
# status.sh
# 
# This script is called by the PSA API when the PSA is requested to ping.
# 
# Return value: 
# ping result
#

COMMAND_OUTPUT="$(ping -c 3 www.google.com)"
echo ${COMMAND_OUTPUT}
exit 1;

