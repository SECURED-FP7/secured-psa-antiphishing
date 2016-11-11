# Tests to be executed in Jenkins. 
In this folder, there is a test set for PSA testing. Only these two files are needed to execute quick smoketest for PSA. For PSA specific tests some modifications have to be done to test scripts.

## Needed modifications for PSA testing
Modifications are needed to I_TC_1.py file. DO NOT MODIFY NEDtest.py. These modifications are also explained in I_TC_1.py comments. The specific lines or functions that need modification are hilighted with comment #PSA SPECIFIC SETTING

### Variables: username and password
Change correct username and password from the beginning of the code in variable list under title 'User terminal settings'

### class test_03_connection
This test class tests connectivity to the Internet and some websites. This class have to be modified according to PSA's policies. Right now there are functions to test that has user access to blocked or allowed website. See I_TC_1.py for detailed instructions.