import os
from dotenv import load_dotenv
from apscheduler.jobstores.memory import MemoryJobStore

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    # ===================================================================================
    # Avoid a warning from the browser that the samesite attribute is
    # being miss-used
    # ===================================================================================
    SESSION_COOKIE_SECURE   = False
    SESSION_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SAMESITE = 'Lax'

    # ===================================================================================
    # Beta override flag
    # ===================================================================================
    BETA_OVERRIDE   = False

    # ===================================================================================
    # region Core info
    # ===================================================================================
    APP_NAME        = 'NUTCase'
    APP_VERSION     = '0.4.0.2'
    UPDATE_HTML     = ''
    GITHUB_API_URL  = "https://api.github.com/repos/ArthurMitchell42/nutcase/"

    # ===================================================================================
    # region Configuration file
    # ===================================================================================
    CONFIG_PATH     = os.path.join(basedir, '../config')
    CONFIG_FILE     = APP_NAME.lower()
    CONFIG_ERROR    = False

    # ===================================================================================
    # region Log file
    # ===================================================================================
    LOGFILE_SUBPATH       = ''
    LOGFILE_NAME          = APP_NAME.lower() + '.log'
    LOGFILE_MAXBYTES      = 250000
    LOGFILE_BACKUPCOUNT   = 10
    LOGFILE_FORMAT        = '%(asctime)s %(levelname)-8s %(module)s: %(message)s'

    DEFAULT_LOGFILE_LEVEL = "INFO"
    DEFAULT_CONSOLE_LEVEL = "INFO"

    # ===================================================================================
    # region Database config
    # ===================================================================================
    DB_SUBPATH              = 'data'
    DB_NAME                 = APP_NAME.lower() + '.db'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                            'sqlite:///' + os.path.join(CONFIG_PATH, DB_SUBPATH, DB_NAME)

    # ===================================================================================
    # region App parameters
    # ===================================================================================
    DOWNLOAD_TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"

    CONFIG_MOD_TIME       = 0.0
    CONFIG_FULLNAME       = ''

    ORDER_METRICS         = True
    COLOURED_LOG          = True
    APC_STRIP_UNITS       = False

    DEFAULT_LOG_LINES     = 20
    CACHE_PERIOD          = 29
    SCRAPE_TIMEOUT        = 15
    POLL_INTERVAL         = 30
    SCAN_DB_INTERVAL      = 30
    SCAN_UPDATE_INTERVAL  = 60  # (Minutes) =  1 hour
    CLEAN_LOG_INTERVAL    = 24  # (Hours)   = 24 hours
    CHART_SAMPLES         = 60
    LOG_RETENTION_DAYS    = 31

    SCRAPE_CACHE          = {}
    WEBHOOKS              = {}

    REWORK                = []
    SERVERS               = []
    CREDENTIALS           = []
    REWORK_VAR_LIST       = []
    APP_STATUS_FLAGS      = {"info": 0, "warning": 0, "alert": 0}

    UI = {
        "FORMAT_RUNTIME": "%-Hh %-Mm %Ss",
        "AUTORANGE_VIN":  True,
        "MIN_RANGE_VIN":  15,
        "AUTORANGE_POW":  True,
        "MIN_RANGE_POW":  8,
        "AUTORANGE_RUN":  True,
        "MIN_RANGE_RUN":  8,
        "LOGFILES_LIST":  14,
    }

    SCHEDULER_JOBS = []
    SCHEDULER_JOBSTORES = {"default": MemoryJobStore()}
    SCHEDULER_TIMEZONE = os.environ.get('TZ') or 'UTC'
    SCHEDULER_JOB_DEFAULTS = {"coalesce": True, "max_instances": 1}

    # Reporting thresholds
    REPORT_BAT_CHARGE_PC = 5
    REPORT_BAT_RUNTIME_S = 120
    REPORT_SCRAPE_LIMIT = 10

# =======================================================================================
# region Derived classes for developement and production
# =======================================================================================
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
