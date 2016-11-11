#!/usr/bin/python
import datetime
import time
import os.path
import json
import calendar
import requests
import urllib2
import logging
import subprocess

logging.basicConfig(filename='/home/psa/pythonScript/PSA.log',level=logging.DEBUG)
entriesFileName = "/home/psa/pythonScript/phishinglist"
tokenFileName = "/home/psa/pythonScript/token.txt"

#logging.basicConfig(filename='PSA.log',level=logging.DEBUG)
#entriesFileName = "./phishinglist"
#tokenFileName = "./token.txt"

token = "a36a8c8977955302f4ae134a5fb7f577150f27a0"

logging.info('Reading the token from %s' % str(tokenFileName))
if(os.path.isfile(tokenFileName)):
	entries = open(tokenFileName)
	token = entries.read()
	token = token.rstrip()
else:
    logging.warning("Token file not found! Using the default one: %s" % str(token))

####
# reconfigure squid
def reconfigure_squid():
    try:
        subprocess.call("/usr/sbin/squid3 -k reconfigure", shell=True)
    except Exception as e:
        logging.warning("squid reconfigure exception\n%s" % (str(e)))

####
#appends the urls retrieved to the file
def appendURLs(entriesFileName, urls_set):
    try:
        entries = open(entriesFileName, "a")
        for i in urls_set:
            try:
                entries.write("^%s\n" % str(i['url']))
            except Exception as e:
                logging.warning("Error in the URL. Error: %s" % str(e))
        entries.close()
    except Exception as e:
        logging.warning("Error appending URLs: %s" % (str(e)))

####
#Retrieves the latest antiphishing url set
def getAPIResults(num_pages):
    try:
        url = "https://api.ecrimex.net/phish?t=%s" % token
        headers = {'Content-Type': 'application/json'}
        #body = { "confidence_lo" : 100, "dd_date_start" : startDate, "dd_date_end" : endDate, "fields" : "url"}
        body = { "confidence_lo" : 100, "fields" : "url"}
        resp = requests.get(url, headers=headers, data=body)
        if resp.status_code is not requests.codes.ok:
            logging.warning("ERROR: get %s response %s" % (str(url),
                                                           str(resp.status_code)))
            return
        output = json.loads(resp.text)
        appendURLs(entriesFileName=entriesFileName, urls_set=output['_embedded']['phish'])
        reconfigure_squid()
    except Exception as e:
        logging.warning("ERROR: GET %s\n%s" % (str(url), str(e)))
    for page in range(1,num_pages):
        try:
            url = "https://api.ecrimex.net/phish?fields=url&page=%s&t=%s"% (str(page), token)
            logging.info("PAGE: %s, url: %s" % (str(page), str(url)))
            socket = urllib2.urlopen(url)
            info = socket.info()
            body = socket.read()
            socket.close()
            appendURLs(entriesFileName=entriesFileName, urls_set=output['_embedded']['phish'])
        except Exception as e:
            logging.warning("Error retrieving page number %s. Error: %s" %
                            (str(page), str(e)))
    reconfigure_squid()
    return

####
# Function that updates the antiphishing URL list
def updateList():
#    try:
#        logging.info("Deleting actual phishing list file at %s" %
#               str(entriesFileName))
#        os.remove(entriesFileName)
#    except Exception as e:
#        logging.info("File %s doesn't exist.\nError: %s" % (str(entriesFileName), str(e)))
#        pass
    numpages = 20
    getAPIResults(num_pages=numpages)
    return

updateList()
