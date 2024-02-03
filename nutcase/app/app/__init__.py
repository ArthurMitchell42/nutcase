import logging
# from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask  
from config import Config_Development # , Config_Production, Config

from app.utils import webhook
from app.utils import configuration
from app.utils import app_log_config

#=================================================
# Initialise components

#==================================================================================================
# Main app creation function
#==================================================================================================
def create_app(config_class=Config_Development):
    app = Flask(__name__)
    app.config.from_object(config_class)

    #====================================================================================
    # Register the app Blueprints
    #====================================================================================
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from app.events import bp as events_bp
    app.register_blueprint(events_bp, url_prefix='/events')

    #====================================================================================
    # Set up the application logging
    #====================================================================================
    app_log_config.Add_Logging_Levels()

    Logfile_Directory = os.path.join(app.config['CONFIG_PATH'], app.config['LOGFILE_SUBPATH'])
    if not os.path.exists(Logfile_Directory):
        os.mkdir(Logfile_Directory)

    app_log_config.Add_RF_Handler( app )

    #====================================================================================
    # Set the logging level from the environment variable LOG_LEVEL if present.
    #====================================================================================
    Console_Level = os.environ.get('LOG_LEVEL', app.config['DEFAULT_CONSOLE_LEVEL']).upper()
    Logfile_Level = os.environ.get('LOG_LEVEL', app.config['DEFAULT_LOGFILE_LEVEL']).upper()

    app.logger.info("Init: Console_Level {} Logfile_Level {}".format( Console_Level, Logfile_Level ))
    app_log_config.Set_Log_Level( app, Console_Level, "con" )
    app_log_config.Set_Log_Level( app, Logfile_Level, "rfh" )
    app.logger.setLevel( 1 )      # Set the root logger to pass everything on
    
    #====================================================================================
    # Load the app configuration from a YAML file
    #====================================================================================
    configuration.Load_Config( app )

    #====================================================================================
    # Log starting and call a web hook
    #====================================================================================
    app.logger.info("{} starting. Version {}, Logging: console {} logfile {}".format(
                app.config['APP_NAME'], app.config['APP_VERSION'],
                logging.getLevelName( app_log_config.Get_Handler( app, 'con' ).level),  
                logging.getLevelName( app_log_config.Get_Handler( app, 'rfh' ).level),  
                ))
    
    webhook.Call_Webhook( app, "ok", { "status": "up", "msg": "NUTCase starting" } )

    return app

from app import models
