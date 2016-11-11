#!/bin/bash
#
# status.sh
#   Created:    18/06/2015
#   Author:     Diego Montero
#   
#   Description:
#       Script that returns the current status of the PSA-squid.
#       TBD the expected returned result (this is an example)...
# 
# This script is called by the PSA API when the PSA's runtime status is requested.
# 
# Return value: 
# 1: PSA is alive
# 0: PSA not running correctly.
#
SERVICE=squid3
if P=$(pgrep $SERVICE)
then
    echo 1
    exit 1
else
    echo 0
    exit 0
    
fi

