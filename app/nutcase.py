#!/usr/bin/env python3
import logging
import logging.handlers

import os                        # For environment variables

import globals
import http_server

#====================================================================================================
# Setup file paths & names from environment variables
#====================================================================================================
Config_Path   = os.environ.get('CONFIG_PATH', "/config")
Log_File      = os.environ.get('LOG_FILE',    "NUTCase.log")
Log_File_Name = os.path.join(Config_Path, Log_File)

if os.environ.get('LOG_REQUESTS', "True").lower() == 'true': Log_Requests = True
else:                                                        Log_Requests = False

if os.environ.get('LOG_REQUESTS_DEBUG', "False").lower() == 'true': Log_Request_Debug = True
else:                                                               Log_Request_Debug = False

if os.environ.get('ORDER_METRICS', "True").lower() == 'true': Order_Metrics = True
else:                                                         Order_Metrics = False

#====================================================================================================
# Main function
#====================================================================================================
def main():
    #================================================
    # Set up logging objects and logging to a file and the console
    #================================================
    log     = logging.getLogger()
    logcons = logging.StreamHandler()

    try:
        logfile = logging.handlers.RotatingFileHandler(Log_File_Name, maxBytes=250000, backupCount=5)
    except Exception as Error:
        log.fatal("Can't open logfile for writing: {} {}".format(Log_File_Name, Error) )
        exit(1)

    Log_Level = os.environ.get('LOG_LEVEL', "INFO").upper()
    if   Log_Level == 'DEBUG':    log.setLevel(logging.DEBUG)
    elif Log_Level == 'INFO':     log.setLevel(logging.INFO)
    elif Log_Level == 'WARNING':  log.setLevel(logging.WARNING)
    elif Log_Level == 'ERROR':    log.setLevel(logging.ERROR)
    elif Log_Level == 'CRITICAL': log.setLevel(logging.CRITICAL)
    elif Log_Level == 'FATAL':    log.setLevel(logging.FATAL)
    else:                         log.setLevel(logging.INFO)

    # Define the format of the log information
    logform = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    logfile.setFormatter(logform)
    logcons.setFormatter(logform)
    log.addHandler(logfile)
    log.addHandler(logcons)

    #================================================
    # Set some main values
    #================================================
    log.info("Program starting. App version is {}, Logging level is {}".format(globals.App_Version, Log_Level) )
    ServerPort = int(os.environ.get('PORT', '9995'))

    #====================================================================================================
    # Launch the web browser
    #====================================================================================================
    http_server.Launch_HTTP_Server( ServerPort )

    return

#====================================================================================================
# Entry point
#====================================================================================================
if __name__ == '__main__':
    main()
