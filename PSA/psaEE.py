#  
#	File: 		psaEE.py
#   Created:    27/08/2014
#   Author:     Francesco Ciaccia
#   
#   Description:
#       Web service running on the PSA interacting with the PSC
#
#

import falcon
import json
import Config
import logging
import subprocess
from execInterface import execInterface
from getConfiguration import getConfiguration
from psaExceptions import psaExceptions
from dumpLogFile import dumpLogFile


#old
conf = Config.Configuration()
date_format = "%m/%d/%Y %H:%M:%S"
log_format = "[%(asctime)s.%(msecs)d] [%(module)s] %(message)s"
logging.basicConfig(filename=conf.LOG_FILE,level=logging.DEBUG,format=log_format, datefmt=date_format)

#older logging
#logging.basicConfig(filename=conf.LOG_FILE,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

pscAddr = conf.PSC_ADDRESS
configsPath = conf.PSA_CONFIG_PATH
psaID = conf.PSA_ID
#confID = conf.CONF_ID

logging.info("--------")
logging.info("PSA EE init.")
logging.info("PSA ID: " + str(psaID)) 
logging.info("PSA NAME: " + str(conf.PSA_NAME)) 
logging.info("PSA VERSION: " + str(conf.PSA_VERSION)) 
logging.info("PSA-PSC API version: " + str(conf.PSA_API_VERSION))
logging.info("PSA log location: " + str(conf.PSA_LOG_LOCATION))
logging.info("--------")

# instantiate class object to manage REST interface to the PSC
execIntf = execInterface(configsPath, conf.PSA_SCRIPTS_PATH, conf.PSA_LOG_LOCATION, psaID)
#confHand = getConfiguration(pscAddr, configsPath, confID, psaID)
confHand = getConfiguration(pscAddr, configsPath, conf.PSA_SCRIPTS_PATH, psaID, str(conf.PSA_API_VERSION))

# start the HTTP falcon proxy and adds reachable resources as routes
app = falcon.API()
#app.add_route('/execInterface', excIntf)
app.add_route("/" + str(conf.PSA_API_VERSION) + '/execInterface/{command}', execIntf)

dumpLog = dumpLogFile()
#FOR DEBUGGING ONLY, REMOVE IN PRODUCTION
app.add_route("/" + str(conf.PSA_API_VERSION) + '/execInterface/dump-log-ctrl', dumpLog)


logging.info("execInterface routes added.") 

# Inform our PSC that we are up
#TODO
'''
try:
    start_res = confHand.send_start_event()
    # We don't need to enable anything
    #proc = subprocess.Popen(confScript, stdout=subprocess.PIPE, shell=True)
    #(out, err) = proc.communicate()
except psaExceptions as exc: 
    pass
'''
# Pull configuration and start the PSA.
try:
    confScript = confHand.pullPSAconf()
    execIntf.callStartScript()
except psaExceptions as exc: 
    pass

logging.info("PSA start done.") 

# http request to ask for the configuration and start the script
'''
try:
    confScript = confHand.pullPSAconf()
    proc = subprocess.Popen(confScript, stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
except psaExceptions as exc: 
    pass
'''
