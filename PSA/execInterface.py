#   
#   File: 		execInterface.py
#	Created:    27/08/2014
#   Author:     Francesco Ciaccia, Jarkko K
#   
#   Description:
#       Web service running on the PSA receiving the configuration for the PSA from the PSC
#
#

import falcon
import logging
import json
import sys
import subprocess
import os
import stat

class execInterface():
    def __init__(self, configsPath, scriptsPath, psaLogLocation, psaID):
        self.confsPath = configsPath
        self.scripts_path = scriptsPath
        self.log_location = psaLogLocation
        self.psaID = psaID
    
    def on_post(self, request, response, command):
        print "onPost"
        try:
            res = {}
            res["command"] = command
            if command == "init":
                # receiev the configuration, or init package
                script_file = self.confsPath + "/psaconf"
                fp=open(script_file, 'wb')
                while True:
                    chunk = request.stream.read(4096)
                    fp.write(chunk)
                    if not chunk:
                        break
                fp.close()

                # Make script executable for current user
                # hazardous.. we're root
                #st = os.stat(script_file)
                #os.chmod(script_file, st.st_mode | stat.S_IEXEC)
                
                # Run the init.sh and return it's return value
                res["ret_code"] = str(self.callInitScript())
                logging.info("PSA "+self.psaID+" configuration registered")
            elif command == "start":
                res["ret_code"] = str(self.callStartScript())
            elif command == "stop":
                res["ret_code"] = str(self.callStopScript())
            else:
                logging.info("POST: unknown command: " + command)
                response.status = falcon.HTTP_404
                return
            
            response.body = json.dumps(res)
            response.status = falcon.HTTP_200
            response.set_header("Content-Type", "application/json")
        except Exception as e:
            logging.exception(sys.exc_info()[0])
            response.status = falcon.HTTP_501

    def on_get(self, request, response, command):
        try:
            res = {}
            res["command"] = command
            if command == "status":
                res["ret_code"] = self.callStatusScript().replace("\n", "")
            elif command == "configuration":
                res["ret_code"] = self.callGetConfigurationScript()
            elif command == "internet":
                res["ret_code"] = self.callGetInternetScript()
            elif command == "log":
                # Return PSA log or 501
                log = self.callGetLogScript()
                if log != None:
                    response.body = log
                    response.status = falcon.HTTP_200
                    response.set_header("Content-Type", "text/plain; charset=UTF-8")
                else:
                    #res["ret_code"] = "not_available"
                    #response.body = json.dumps(res)
                    #response.set_header("Accept", "application/json")
                    response.status = falcon.HTTP_501
                return
            else:
                logging.info("GET: unknown command: " + command)
                response.status = falcon.HTTP_404
                return
            
            response.body = json.dumps(res)
            response.status = falcon.HTTP_200
            response.set_header("Content-Type", "application/json")
        except Exception as e:
            logging.exception(sys.exc_info()[0])
            response.status = falcon.HTTP_501

    def callInitScript(self):
        logging.info("callInitScript()")
        ret = subprocess.call(['.' + self.scripts_path + 'init.sh'])
        return ret
    
    def callStartScript(self):
        logging.info("callStartScript()")
        ret = subprocess.call(['.' + self.scripts_path + 'start.sh'])
        return ret

    def callStopScript(self):
        logging.info("callStopScript()")
        ret = subprocess.call(['.' + self.scripts_path + 'stop.sh'])
        return ret

    def callStatusScript(self):
        proc = subprocess.Popen(['.' + self.scripts_path + 'status.sh'], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        return out
    
    def callGetConfigurationScript(self):
        logging.info("callGetConfigurationScript()")
        proc = subprocess.Popen(['.' + self.scripts_path + 'current_config.sh'], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        return out

    def callGetInternetScript(self):
        logging.info("callGetInternetScript()")
        proc = subprocess.Popen(['.' + self.scripts_path + 'ping.sh'], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        return out
    
    def callGetLogScript(self):
        logging.info("callGetLogScript()")
        ret = None
        try:
            with open(self.log_location, "r") as f:
                ret = f.read()
        except Exception as e:
            logging.exception(sys.exc_info()[0])
        
        return ret
    
    def get_client_address(self,environ):
        try:
            return environ['HTTP_X_FORWARDED_FOR'].split(',')[-1].strip()
        except KeyError:
            return environ['REMOTE_ADDR']

