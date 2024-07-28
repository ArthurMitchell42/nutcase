import logging
import os
import sys
import signal

from flask import Flask
from config import Config_Development  # Config_Production

from app.utils import webhook
from app.utils import configuration
from app.utils import app_log_config

from app.flask_scheduler import FlaskSchedulerManager

import threading
from queue import Queue

from app.cache_controller.cache_controller import Cache_Handler

from flask_sqlalchemy import SQLAlchemy

# ========================================================================================
# Initialise components
# ========================================================================================
db = SQLAlchemy()
scheduler = FlaskSchedulerManager()
Stop_Event = threading.Event()

# ========================================================================================
# exit_handler - called with ctrl-c to shutdown the threads
# ========================================================================================
def exit_handler(signal, frame):
    print('Exiting')
    Stop_Event.set()
    scheduler.shutdown()
    sys.exit(0)

# ========================================================================================
# Main app creation function
# ========================================================================================
def create_app(config_class=Config_Development):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ====================================================================================
    # Register the app Blueprints
    # ====================================================================================
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from app.events import bp as events_bp
    app.register_blueprint(events_bp, url_prefix='/events')

    # ====================================================================================
    # Set up the application logging
    # ====================================================================================
    app_log_config.Add_Logging_Levels()

    Logfile_Directory = os.path.join(app.config['CONFIG_PATH'], app.config['LOGFILE_SUBPATH'])
    if not os.path.exists(Logfile_Directory):
        os.mkdir(Logfile_Directory)

    app_log_config.Add_RF_Handler(app)

    # ====================================================================================
    # Set the logging level from the environment variable LOG_LEVEL if present.
    # ====================================================================================
    Console_Level = os.environ.get('LOG_LEVEL', app.config['DEFAULT_CONSOLE_LEVEL']).upper()
    Logfile_Level = os.environ.get('LOG_LEVEL', app.config['DEFAULT_LOGFILE_LEVEL']).upper()
    app_log_config.Set_Log_Level(app, Console_Level, "con")
    app_log_config.Set_Log_Level(app, Logfile_Level, "rfh")
    app.logger.setLevel(1)      # Set the root logger to pass everything on

    # ====================================================================================
    # Load the app configuration from a YAML file
    # ====================================================================================
    with app.app_context():
        configuration.Load_Config()

    # ===================================================================================
    # Define database components
    # ===================================================================================
    db.init_app(app)
    # migrate.init_app(app, db)

    DB_Directory = os.path.join(app.config['CONFIG_PATH'], app.config['DB_SUBPATH'])
    if not os.path.exists(DB_Directory):
        os.mkdir(DB_Directory)

    with app.app_context():
        db.create_all()

    # ====================================================================================
    # APPScheduler
    # ====================================================================================
    scheduler.init_app(app, console_handler=False)
    # with app.app_context():
    #     db_engine = db.get_engine()
    #     scheduler.add_jobstore('sqlalchemy', engine=db_engine)

    scheduler.start()
    thread_console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(threadName)s: %(message)s')
    thread_console_handler.setFormatter(formatter)
    scheduler.queuelistener(thread_console_handler)

    # ====================================================================================
    # Start independant threads
    # ====================================================================================
    app.config['CACHE_QUEUE'] = Queue()
    app.config['STOP_CACHE'] = Stop_Event

    # Spawn the cache handler to answer requests down the queue
    app.config['PROC_CACHE_HANDLER'] = scheduler.add_job(Cache_Handler, args=[app])

    # Spawn the server poller to generate requests down the queue at intervals
    app.config['PROC_SERVER_POLLER'] = scheduler.add_job(Server_Poll, "interval",
                                            seconds=app.config['POLL_INTERVAL'], args=[app])

    # Scan the DB to update the 3 status icons
    app.config['PROC_SCAN_DB'] = scheduler.add_job(Scan_DB, "interval",
                                            seconds=app.config['SCAN_DB_INTERVAL'], args=[app])

    # Spawn the server poller to generate requests down the queue at intervals
    app.config['PROC_GET_UPDATE'] = scheduler.add_job(Set_Config_Update_String, "interval",
                                            minutes=app.config['SCAN_UPDATE_INTERVAL'], args=[])

    # Spawn the server poller to generate requests down the queue at intervals
    app.config['PROC_CLEAN_LOGS'] = scheduler.add_job(Clean_Old_Logs, "interval",
                                            hours=app.config['CLEAN_LOG_INTERVAL'],
                                            args=[app.config['LOG_RETENTION_DAYS']])
    # Starup actions
    Scan_DB(app)

    with app.app_context():
        Clean_Old_Logs(app.config['LOG_RETENTION_DAYS'])
        Set_Config_Update_String()

    signal.signal(signal.SIGINT, exit_handler)

    # ====================================================================================
    # Log starting and call a web hook
    # ====================================================================================
    app.logger.info("{} starting. Version {}, Logging: console {} logfile {}".format(
        app.config['APP_NAME'], app.config['APP_VERSION'],
        logging.getLevelName(app_log_config.Get_Handler(app, 'con').level),
        logging.getLevelName(app_log_config.Get_Handler(app, 'rfh').level),
        ))

    webhook.Call_Webhook(app, "ok", {"status": "up", "msg": "NUTCase starting"})

    return app

from app.utils.db_utils import Scan_DB                  # noqa: E402
from app.poller.poller import Server_Poll               # noqa: E402
from app.api.api_utils import Set_Config_Update_String  # noqa: E402
from app.utils.db_utils import Clean_Old_Logs           # noqa: E402
