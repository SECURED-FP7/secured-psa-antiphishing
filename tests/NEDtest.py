'''
This library contains functions to execute NED test scripts
'''

import time
import selenium, re
from selenium import webdriver

####################################
#TEST CONNECTION AND LOGGING IN/OUT#
####################################

def login(driver, username, password, login_address):
	try:
		driver.get(login_address)
	except:
		print "In webpage title: %s" % driver.title
		assert 0, timeout(login_address)
	driver.find_element_by_id("input-username").clear()
	driver.find_element_by_id("input-username").send_keys(username)
	driver.find_element_by_id("input-password").clear()
	driver.find_element_by_id("input-password").send_keys(password)
	driver.find_element_by_id("submit").click()


def allowedWebpage(driver, webpage):
	try:
		driver.get(webpage)
	except:
		print "In webpage title: %s" % driver.title
		assert 0, timeout(webpage)

def blockedWebpage(driver, webpage, title):
	timeout = 'FALSE'
	try:
		driver.get(webpage)
	except:
		timeout = 'TRUE'
	print 'Website title: %s' % driver.title
	print 'Expected website title: %s' % title
	print 'Timeout occured: %s' % timeout
	if title in driver.title:
		assert 0, notBlocked(webpage)
	elif timeout == 'FALSE':
		assert 0, problemLoading(driver.title, webpage)
	return timeout

def connectionNotloggedin(driver):
	webpage = 'http://www.secured-fp7.eu'
	title = 'SECURED'
	timeout = 'FALSE'
	try:
		driver.get(webpage)
	except:
		timeout = 'TRUE'
	if title in driver.title:
		assert 0, 'User had access to SECURED website before logging in to NED'
	elif timeout == 'FALSE':
		assert 0, problemLoading(driver.title, webpage)
	return timeout

def getUserIPfromPSC(driver, manager_address):
	userIP = ''

	try:
		driver.get(manager_address)
	except:
		print "In webpage title: %s" % driver.title
		assert 0, timeout(manager_address)
	try:
		userIP = driver.find_element_by_id("user-ip").text
	except:
		print "In webpage title: %s" % driver.title
		assert 0, 'Could not found element \"user-ip\" from %s' % manager_address
	print "User\'s IP is: %s" % userIP
	return userIP

def checkSECUREDok(driver, manager_address):
	manager_counter = 0
	time_counter = 0
	counter_timeout = 60
	interval = 5
	status_text = ''
	start_time = 0.000

	start_time = time.time()
	while True:
		try:
			driver.get(manager_address)
			if manager_counter >= counter_timeout:
				print "Try: In webpage title: %s" % driver.title
				assert 0, timeout(manager_address)
			if driver.title != 'Problem loading page':
				break
			else:
				time.sleep(interval)
				manager_counter += interval
		except:
			if manager_counter >= counter_timeout:
				print "Except: In webpage title: %s" % driver.title
				assert 0, timeout(manager_address)
			time.sleep(interval)
			manager_counter += interval
	while True:
		try:
			status_text = driver.find_element_by_id("status").text
		except:
			if time_counter >= counter_timeout:
				assert 0, 'Could not found status text. Status text: %s' % (status_text)
			time.sleep(interval)
			time_counter += interval
			
		if 'wait' in status_text:
			if time_counter >= counter_timeout:
				assert 0, 'It took over %d seconds to load PSA(s)\n %s' % (counter_timeout, status_text)
			time.sleep(interval)
			time_counter += interval
		elif 'OK' in status_text:
			print 'It took %.3f seconds to load PSA(s)' % (time.time() - start_time)
			break
		elif 'Error' in status_text:
			print driver.find_element_by_id('page').text
			assert 0, 'Text error in status text'

#########
#LOGGING#
#########

def getLogAddress(driver, manager_address, log_address):
	ip = []
	ip_list = []
	try:
		driver.get(manager_address)
	except:
		print "In webpage title: %s" % driver.title
		timeout(manager_address)
	try:
		ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', driver.find_element_by_id("psa-list-online").text)
	except:
		print "Not able to found IP number from element psa-list-online"
		print "In webpage title: %s" % driver.title
	for x in ip:
		ip_list.append(log_address + x)
	return ip_list

def writeLog(driver, logPath, logAddress):
	logFile = open(logPath, 'w+')
	try:
		driver.get(logAddress)
	except:
		print "In webpage title: %s" % driver.title
		timeout(logAddress)
	try:
		logFile.write(driver.find_element_by_xpath('/html/body/pre').text + '\n')
	except:
		print "Not able to write dump log file from %s to %s" % (logAddress, logPath)
	logFile.close()


################
#ERROR HANDLING#
################

def timeout(url):
        print "Could not load page %s. Connection timed out." % url

def notBlocked(url):
        print "User had access to blocked page %s." % url

def problemLoading(title, webpage):
	print '\"%s\" reported in %s title. Connection should timeout.' % (title, webpage)

def emptyList(listname):
	print "IP address list %s is empty." % listname

def titleNotfound(expected, found):
	print 'Text \"%s\" not found in webpage title. Found \"%s\" instead' % (expected, found)
