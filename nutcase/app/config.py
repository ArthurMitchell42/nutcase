import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    #==================================================================
    # Avoid a warning from the browser that the samesite attribute is
    # being miss-used
    #==================================================================
    SESSION_COOKIE_SECURE   = False
    SESSION_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SAMESITE = 'Lax'

    #==================================================================
    # Beta override flag
    #==================================================================
    BETA_OVERRIDE         = False

    #==================================================================
    # Core info
    #==================================================================
    APP_NAME              = 'NUTCase'
    APP_VERSION           = '0.3.0'

    #==================================================================
    # Configuration file
    #==================================================================
    CONFIG_PATH           = os.path.join(basedir, '../config' ) 
    CONFIG_FILE           = APP_NAME.lower()

    #==================================================================
    # Log file
    #==================================================================
    LOGFILE_SUBPATH       = ''
    LOGFILE_NAME          = APP_NAME.lower() + '.log'
    LOGFILE_MAXBYTES      = 250000
    LOGFILE_BACKUPCOUNT   = 10
    LOGFILE_FORMAT        = '%(asctime)s %(levelname)-8s %(module)s: %(message)s'

    DEFAULT_LOGFILE_LEVEL = "INFO"
    DEFAULT_CONSOLE_LEVEL = "INFO"

    #==================================================================
    # App parameters
    #==================================================================
    DOWNLOAD_TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"

    CONFIG_MOD_TIME       = int
    CONFIG_FULLNAME       = ''

    ORDER_METRICS         = True
    COLOURED_LOG          = True
    APC_STRIP_UNITS       = False

    DEFAULT_LOG_LINES     = 20
    CACHE_PERIOD          = 30
    CHART_SAMPLES         = 60

    SCRAPE_CACHE          = {}
    WEBHOOKS              = {}

    REWORK                = []
    SERVERS               = []
    CREDENTIALS           = []
    REWORK_VAR_LIST       = []

    APP_STATUS_FLAGS      = {
        "info":     0,
        "warning":  0,
        "alert":    0
    }

    UI = {
        "FORMAT_RUNTIME": "%-Hh %-Mm %Ss",
        "AUTORANGE_VIN" : True,
        "MIN_RANGE_VIN" : 15,
        "AUTORANGE_POW" : True,
        "MIN_RANGE_POW" : 8,
        "AUTORANGE_RUN" : True,
        "MIN_RANGE_RUN" : 8,
    }

#======================================================================
#   Class functions
#======================================================================

#======================================================================
# Derived classes for developement and production
#======================================================================
class Config_Development(Config):
    CONFIG_SET = 'Dev'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uUwb-C58lzujc3Xn0hZ8c48iHw-VA341'
    DEBUG = True
    TESTING = False
    
class Config_Production(Config):
    CONFIG_SET = 'Prd'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uUwb-C58lzujc3Xn0hZ8c48iHw-VA341'
    DEBUG = False
    TESTING = False
