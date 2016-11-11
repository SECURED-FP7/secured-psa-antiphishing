'''
I_TC_1: Network Edge Device (NED) Functional operation

1. User authentication and Attestation:
	a) Test connection to NED (class test_01)
	b) Test logging in with invalid username (class test_01)
	c) Test logging in with invalid password (class test_01)
	d) Test logging in with valid username and password (class test_01)
	e) Test Internet connection (class test_03)
2. Setup of New user (specs from D6.1)
	a) Handle new user (class test_02)
	b) Retrieve user specific data, e.g. profile (class test_04)
	c) Setup new user trusted virtual domain (TVD), which includes his/hers PSC (class test_02)
	d) Request user policies (class test_03)
	e) Setup and configure user PSAs (class test_02)

Preconditions to this test set:
- One user terminal is powered on and Selenium server is started
- NED is powered on

Before tests (setup_module), script opens web browser Firefox on User terminal
After tests (teardown_module), script closes the browser on User terminal

PSA specific settings:
- in program code, these codelines are hilighted with #PSA SPECIFIC SETTING
- From variable list 'User terminal settings', set appropriate username and password
- Check whole class test_03_connection

'''

import NEDtest
import selenium, time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from nose.plugins.skip import Skip, SkipTest
from nose.tools import with_setup

#NED settings
login_address = 'http://10.2.2.253:8080/login'
manager_address = 'http://10.2.2.251:8080/psc'
PSAlog_prefix = 'http://10.2.2.251:8080/psa/dump-log-psa-ctrl/'
PSClog_address = 'http://10.2.2.251:8080/psc/dump-log-psc'

#User terminal settings
user_ip = '192.168.184.129'
user_address = 'http://' + user_ip + ':4444/wd/hub'
username = 'test' #PSA SPECIFIC SETTING
password = 'secuser' #PSA SPECIFIC SETTING
logPath_prefix = '/var/lib/jenkins/logs/builds/I_TC_1/'

#Variables
driver = 0
website_timeout = 60 #seconds
PSXload_time = 0.000
startTime = 0.000



def setup_module(module):
	#Setup WebDriver
	global driver
	driver = webdriver.Remote(command_executor=user_address, desired_capabilities=webdriver.DesiredCapabilities.FIREFOX)
	driver.set_page_load_timeout(website_timeout)

def teardown_module(module):
	#Write PSA logfile
	PSAlog_address = NEDtest.getLogAddress(driver, manager_address, PSAlog_prefix)
	if PSAlog_address:
		for x in range(len(PSAlog_address)):
			NEDtest.writeLog(driver, logPath_prefix + 'PSA' + str(x) + '.log', PSAlog_address[x])
	else:
		NEDtest.emptyList('PSAlog_address')
	#Write PSC logfile
	NEDtest.writeLog(driver, logPath_prefix + 'PSC.log', PSClog_address)
	#Write parameters logfile
	paraFile = open(logPath_prefix + 'parameters.log', 'w+')
	paraFile.write('File created: %s\n' % time.ctime())
	paraFile.write('Test I_TC_1 with username %s\n' % username)
	paraFile.write('User terminal IP: %s\n' % user_ip)
	paraFile.write('NED login address: %s\n' % login_address)
	paraFile.write('PSC manager address: %s\n' % manager_address)
	paraFile.write('PSA log address: %s\n' % PSAlog_address)
	paraFile.write('PSC log address: %s\n' % PSClog_address)
	paraFile.write('Timeout of website connection: %s seconds\n' % website_timeout)
	paraFile.write('Loading time from login to "SECURED: OK": %.3f seconds\n' % PSXload_time)
	paraFile.close()
	#Close WebDrive
	driver.close()
	driver.quit()



class test_01_login:
	#This test set tests logging in with invalid credentials and
	#valid credentials. No need to modify for PSA testing

	skipNext = 0

	def setup(self):
		try:
			driver.get(login_address)
		except:
			assert 0, NEDtest.timeout(login_address)

	def test_01_connectionNED(self):
		assert "NED" in driver.title, NEDtest.titleNotfound('NED', driver.title)

	def test_02_noconnectionInternet(self):
		timeout = NEDtest.connectionNotloggedin(driver)
		assert timeout == 'TRUE', "User had access to Internet before logging in to NED"

	def test_03_invalidUsername(self):
		NEDtest.login(driver, 'invalidusername', password, login_address)
		assert "Login failed" in driver.find_element_by_id("error-msg").text, "No Login failed -message in element error-msg"

	def test_04_invalidPassword(self):
		NEDtest.login(driver, username, 'invalidpassword', login_address)
		assert "Login failed" in driver.find_element_by_id("error-msg").text, "No Login failed -message in element error-msg"

	def test_05_successfulLogin(self):
		NEDtest.login(driver, username, password, login_address)
		assert "Congratulations" in driver.find_element_by_id("login_ok").text, "No Congratulations-message in element login_ok"

	def test_06_logout(self):
		try:
			driver.find_element_by_id("logout").click()
		except:
			test_01_login.skipNext = 1
			assert 0, 'Could not found element \"logout\" from %s' % login_address
		assert "Logged out" in driver.find_element_by_id("logout_ok").test, "No Logged out -message in webpage"

	def test_07_login(self):
		if test_01_login.skipNext == 1:
			raise SkipTest('Skip re-login because logout test failed')
		NEDtest.login(driver, username, password, login_address)
                assert "Congratulations" in driver.find_element_by_id("login_ok").text, "No Congratulations-message in element login_ok"
	

class test_02_checkSECUREDok:
	#This test set tests that are PSC and PSA(s) started correctly and
	#are they visible in PSC GUI. No need to modify for PSA testing

	def setup(self):
		global startTime
		driver.get('about:blank')
		startTime = time.time()

	def teardown(self):
		global PSXload_time
		PSXload_time = time.time() - startTime

	def test_01_checkSECUREDok(self):
		NEDtest.checkSECUREDok(driver, manager_address)


class test_03_connection:
	#This test set tests user's connection to Internet and websites.
	#This set have to be modified to match PSA policies

	############################################
	#PSA SPECIFIC SETTINGS (ALMOST WHOLE CLASS)#
	############################################

	def setup(self):
		driver.get('about:blank')

	def test_01_internetConnection(self):
		NEDtest.allowedWebpage(driver, 'http://www.secured-fp7.eu')
		assert "SECURED" in driver.title, NEDtest.titleNotfound('SECURED', driver.title)

	def test_02_blockedConnectionPolito(self): #PSA SPECIFIC SETTINGS
		#With this test case you can check that blocked webpage from PSA is really blocked.
		#Copy-paste this function to create new tests cases to different blocked pages.
		#See example test_03_allowedConnectionUPC and test_04_allowedConnectionGoogle
		website_address = 'http://www.polito.it'
		website_title = 'Politecnico di Torino'
		timeout = NEDtest.blockedWebpage(driver, website_address, website_title)
		assert timeout == 'TRUE', "Connecting to blocked site %s did not timeout. Could be general error in Internet connection." % website_address

	def test_03_allowedConnectionUPC(self): #PSA SPECIFIC SETTINGS
		#With this function you can test pages where user has access
		#Copy-paste this function to create new tests cases to different blocked pages.                                           
		#See example test_03_allowedConnectionUPC and test_04_allowedConnectionGoogle
		website_address = 'http://www.upc.edu'
		website_title = 'UPC'
		NEDtest.allowedWebpage(driver, website_address)
		assert website_title in driver.title, NEDtest.titleNotfound(website_title, driver.title)

	def test_04_allowedConnectionGoogle(self): #PSA SPECIFIC SETTINGS
		website_address = 'http://www.google.com'
		website_title = 'Google'
		NEDtest.allowedWebpage(driver, website_address)
		assert website_title in driver.title, NEDtest.titleNotfound(website_title, driver.title)

class test_04_userData:
	#This test set checks user's data from PSC GUI. Right now, it only
	#checks that user's IP is in correct form

	def test_01_checkuserIP(self):
		userIP = NEDtest.getUserIPfromPSC(driver, manager_address)
		assert "10.2.2." in userIP, "Could not retrieve user IP from PSC"
