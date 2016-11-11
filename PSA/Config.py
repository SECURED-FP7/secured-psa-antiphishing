import ConfigParser
import os
import copy


class Configuration(object):
    
    _instance = None
    #(fmignini) Not too meaningful use this var, I should change his name with something else like inizialized = False 
    _AUTH_SERVER = None
    
    def __new__(cls, *args, **kwargs):
        
        if not cls._instance:
            cls._instance = super(Configuration, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance 
    
    def __init__(self):
        #print 'Configuration - PATH : '+os.getcwd()
        path = copy.copy(os.getcwd())
        path_dirs = path.split("/")
        for path_dir in path_dirs:
            if path_dir == 'tests':
                self.test = True
            else:
                self.test = False
        #print self.test
        if self._AUTH_SERVER is None:
            self.inizialize()
    
    def inizialize(self): 
        config = ConfigParser.RawConfigParser()
        config.read('psaEE.conf')
        self._LOG_FILE = 'PSA.log'
        self._VERBOSE = 'true'
        self._DEBUG = 'true'
        self._PSC_ADDRESS = config.get('configuration', 'psc_address')
        self._PSA_CONFIG_PATH = config.get('configuration', 'psa_config_path')
        self._PSA_ID = config.get('configuration', 'psa_id')
        self._PSA_SCRIPTS_PATH = config.get('configuration', 'scripts_path')
        self._PSA_API_VERSION = config.get('configuration', 'psa_api_version')
        self._PSA_VERSION = config.get('configuration', 'psa_version')
        self._PSA_NAME = config.get('configuration', 'psa_name')
        self._PSA_LOG_LOCATION = config.get('configuration', 'psa_log_location')
        
        #self._CONF_ID = config.get('configuration', 'conf_id')

    @property
    def LOG_FILE(self):
        return self._LOG_FILE

    @property
    def VERBOSE(self):
        return self._VERBOSE

    @property
    def PSC_ADDRESS(self):
        return self._PSC_ADDRESS

    @property
    def PSA_CONFIG_PATH(self):
        return self._PSA_CONFIG_PATH

    @property
    def PSA_SCRIPTS_PATH(self):
        return self._PSA_SCRIPTS_PATH

    @property
    def PSA_ID(self):
        return self._PSA_ID
    
    @property
    def PSA_NAME(self):
        return self._PSA_NAME

    @property
    def PSA_API_VERSION(self):
        return self._PSA_API_VERSION
    
    @property
    def PSA_VERSION(self):
        return self._PSA_VERSION
    
    @property
    def PSA_LOG_LOCATION(self):
        return self._PSA_LOG_LOCATION

    # @property
    # def CONF_ID(self):
    #     return self._CONF_ID
