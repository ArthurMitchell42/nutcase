import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask  
from config import Config_Development # , Config_Production, Config
# from flask_moment import Moment  # https://momentjs.com/

from app.api import webhook
from app.api import configuration

#=================================================
# Initialise components
#
# moment = Moment()

#==================================================================================================
# Add_Level function
#==================================================================================================
def Add_Logging_Levels():
    DEBUGV_LEVEL_NUM = 9 
    DEBUGVV_LEVEL_NUM = 8 

    logging.addLevelName(DEBUGV_LEVEL_NUM, "DEBUGV")
    logging.addLevelName(DEBUGVV_LEVEL_NUM, "DEBUGVV")

    def debugv(self, message, *args, **kws):
        if self.isEnabledFor(DEBUGV_LEVEL_NUM):
            self._log(DEBUGV_LEVEL_NUM, message, args, **kws) 

    def debugvv(self, message, *args, **kws):
        if self.isEnabledFor(DEBUGVV_LEVEL_NUM):
            self._log(DEBUGVV_LEVEL_NUM, message, args, **kws) 

    logging.Logger.debugv = debugv
    logging.Logger.debugvv = debugvv
    return

#==================================================================================================
# Main app creation function
#==================================================================================================
def create_app(config_class=Config_Development):
    app = Flask(__name__)
    app.config.from_object(config_class)

    #====================================================================================
    # Define the app Blueprints
    #====================================================================================
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from app.events import bp as events_bp
    app.register_blueprint(events_bp, url_prefix='/events')

    #====================================================================================
    # Set up email for the application log
    #====================================================================================
    # if not app.debug and not app.testing:
    #     if app.config['MAIL_SERVER']:
    #         auth = None
    #         if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
    #             auth = (app.config['MAIL_USERNAME'],
    #                     app.config['MAIL_PASSWORD'])
    #         secure = None
    #         if app.config['MAIL_USE_TLS']:
    #             secure = ()
    #         mail_handler = SMTPHandler(
    #             mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
    #             fromaddr='no-reply@' + app.config['MAIL_SERVER'],
    #             toaddrs=app.config['MAIL_DEFAULT_SENDER'], subject=app.config['MAIL_DEFAULT_SUBJECT'] + " " + 'App Failure',
    #             credentials=auth, secure=secure)
    #         mail_handler.setLevel(logging.ERROR)
    #         app.logger.addHandler(mail_handler)

    #====================================================================================
    # Set up the application log file
    #====================================================================================
    Logfile_Directory = os.path.join(app.root_path, app.config['LOGFILE_RELATIVE_PATH'])
    if not os.path.exists(Logfile_Directory):
        os.mkdir(Logfile_Directory)
    Logfile_Fullname = os.path.join(Logfile_Directory, 'nutcase.log')

    Logfile_Handler = RotatingFileHandler(Logfile_Fullname, maxBytes=250000, backupCount=10)
    Log_Format = '%(asctime)s %(levelname)-8s %(module)s: %(message)s'
    Logfile_Handler.setFormatter(logging.Formatter(Log_Format))
    Logfile_Handler.name = "logfile_handler"
    app.logger.addHandler(Logfile_Handler)

    Add_Logging_Levels()

    #====================================================================================
    # Set the logging level from the environment variable LOG_LEVEL if present.
    #====================================================================================
    try:              app.logger.setLevel( os.environ.get('LOG_LEVEL', "DEBUG").upper() )
    except Exception: app.logger.setLevel( logging.DEBUG )

    #====================================================================================
    # Load the app configuration from a YAML file
    #====================================================================================
    configuration.Load_Config( app )

    #====================================================================================
    # Log starting and call a web hook
    #====================================================================================
    app.logger.info("{} starting. Version {}, Logging level {}".format(
                        app.config['APP_NAME'], app.config['APP_VERSION'], 
                        logging.getLevelName(app.logger.level)).lower() )

    webhook.Call_Webhook( app, "ok", { "status": "up", "msg": "NUTCase starting" } )

    return app

from app import models
