#!/bin/bash
#
# This script copies the PSA codes into the NED v0.6 implementation folders, namely:
# 1) PSCM/userList
# 2) TVDM/psaConfigs/[psaID] folder
# 3) TVDM/PSAManifest/[psaID] file
# 4) TVDM/userGraph/[psaID] file
#
# One parameter is required - the full path to your destination NED v0.5.1 dir, e.g., /home/ned/NED/.
# Note: This will overwrite existing configurations for the PSA_ID and the USER inside your NED!

if [ $# -ne 1 ] ; then
	echo "Usage: $0 [Full path to NED directory where the PSA files are to be copied (e.g., /home/ned/NED/)]"
	exit 1
fi

NED_VERSION=v0.5.1

# Note: If you use this for other PSAs, please rename the PSA_ID as such (the config folders have to match in NED_files/TVDM/)!
PSA_ID="antiphishingPSA"
USER="test"
PW=" secuser"
PSCM_PATH=$1PSCM/
NED_PATH=$1
USER_LIST=userList

TEMPLATES=NED_files_template/TVDM/

if [ ! -f $PSCM_PATH$USER_LIST ]; then
echo "$PSCM_PATH$USER_LIST file does not exist."
echo "Usage: $0 [full path to NED directory where the PSA files are to be copied (e.g., /home/ned/NED/)]"
	exit 1
fi

# 1
#################################################################################
echo "Checking if PSA user exists in PSCM/userList"
user_pw=" secuser"
user_cred=$PSA_ID$user_pw

if grep -q "$USER" $PSCM_PATH"$USER_LIST"; then
    echo "User existed in PSCM/userList, skipping creation of new user."
else
    echo "User not in PSCM/userList file, creating new user."
    echo $USER$PW >> $PSCM_PATH$USER_LIST
fi

# 2
#################################################################################
echo "Copying PSA files into NED $NED_VERSION folders"
cp -avr NED_files/TVDM $NED_PATH

