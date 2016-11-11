#  
#   File: 	getConfiguration.py
#   Created:    05/09/2014
#   Author:     Francesco Ciaccia

#   Modified:    29/10/2015
#   Author:     Jarkko Kuusijarvi
#   
#   Description:
#       Web service running on the PSA interacting with the PSC
#
#

import json
import requests
import logging
from psaExceptions import psaExceptions
import subprocess
import base64

class getConfiguration():

    #def __init__(self, pscAddr, configsPath, confID, psaID):
    def __init__(self, pscAddr, configsPath, scriptsPath, psaID, psaAPIVersion):
        self.pscAddr = pscAddr
        self.configsPath = configsPath
        self.scripts_path = scriptsPath
        #self.confID = confID
        self.psaID = psaID
        self.psaAPI = psaAPIVersion

    def send_start_event(self):
        logging.info("PSA: send_start_event")
        logging.info("PSA: "+self.psaID+" calling PSC")
        resp = requests.get(self.pscAddr + "/" + self.psaAPI + "/psa_up/" + self.psaID)
        logging.info("PSA: "+self.psaID+" calling PSC done")
        return resp.content

    def pullPSAconf(self):

        header = {'Content-Type':'application/octet-stream'}

        #resp = requests.get(self.pscAddr+"/getConf/"+self.psaID+"/"+self.confID, headers=header)
        resp = requests.get(self.pscAddr + "/" +self.psaAPI + "/getConf/"+self.psaID, headers=header)
        if (resp.status_code == requests.codes.ok):
            #fp=open(self.configsPath+"/"+self.confID,'wb')
            #fp=open(self.configsPath+"/"+self.psaID,'wb')
            # We don't have multiple security controls inside one PSA image at the moment.
            json_config = False
            try:
                conf = json.loads(resp.content)
                logging.info("PSA JSON conf received:")
                logging.info(conf)
                # Handle different config formats
                if conf["conf_type"] == "base64":
                    decoded_conf = base64.b64decode(conf["conf"])
                elif conf["conf_type"] == "text":
                    decoded_conf = conf["conf"]
                else:
                    # Use default format, presume text.
                    decoded_conf = conf["conf"]
                json_config = True
            except Exception as e:
                logging.info("Could not load JSON config, reverting to old text format")
                decoded_conf = resp.content
            
            fp=open(self.configsPath+"/psaconf", 'wb')
            fp.write(decoded_conf)
            fp.close()
            
            params = {x: conf[x] for x in conf if x not in ['conf','conf_type']}
 
            with open(self.configsPath+"/psaparams.json", 'wb') as f:
                json.dump(params, f)
            logging.info("PSA parameters: %s" % (str(params)))
           
            self.callInitScript()
            if json_config:
                self.enforceConfiguration(conf)
            
            logging.info("PSA "+self.psaID+" configuration registered")
            return resp.content
        else: 
            logging.error("Bad configuration request for PSA "+self.psaID)
            raise psaExceptions.confRetrievalFailed()


        # header = {'Accept':'application/octet-stream', 'Content-Type':'application/octet-stream'}   
        # resp = requests.get(self.pscAddr+"/getConfiguration/"+self.confURI, data={}, headers=header)
        # if (resp.status_code != 200):
     	# 	msg = "PSC is not able to provide the conf for: [PSAid] " + self.psaID + ", [confURI] " + self.confURI
        # 	raise psaExceptions.confRetrievalFailed(msg)

            # TODO check script validity
        #return resp.text

    def callInitScript(self):
        logging.info("callInitScript()")
        ret = subprocess.call(['.' + self.scripts_path + 'init.sh'])
        return ret

    def enforceConfiguration(self, jsonConf):
        req_keys = ("IP", "dns", "netmask", "gateway")
        has_req = False
        if all (key in jsonConf for key in req_keys):
            has_req = True
        
        if has_req:
            logging.info("PSA requires IP, configuring...")
            ip = jsonConf["IP"]
            dns = jsonConf["dns"]
            netmask = jsonConf["netmask"]
            gateway = jsonConf["gateway"]
            logging.info("ip: " + str(ip))
            logging.info("gateway: " + str(gateway))
            logging.info("dns: " + str(dns))
            logging.info("netmask: " + str(netmask))
            ret = subprocess.call(['.' + self.scripts_path + 'ip_conf.sh', ip, gateway, dns, netmask])
            logging.info("Result of setting config: " + str(ret))
        else:
            logging.info("PSA doesn't require IP, skipping configuration.")
