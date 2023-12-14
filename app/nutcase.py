#!/usr/bin/env python3
#==================================================================================================
# 
#                                   NUTCase
# 
#  A multi-purpose interface between NUT-Tools or APC Daemon servers and the Prometheus/Grafana
#    data logging system and JSON consumers such as HomePage.
#
#==================================================================================================
import logging
import logging.handlers
import os

import globals
import http_server
import configuration

#==================================================================================================
# Set up logging objects and logging to a file and the console
#==================================================================================================
def Configure_Log(log):
    try:              log.setLevel( os.environ.get('LOG_LEVEL', "DEBUG").upper() )
    except Exception: log.setLevel( logging.DEBUG )

    Log_Console_Handler = logging.StreamHandler()

    Log_Filename     = os.environ.get('LOG_FILE', "nutcase.log")
    globals.Log_File = os.path.join(globals.Config_Path, Log_Filename)
    try:
        Log_File_Handler = logging.handlers.RotatingFileHandler(globals.Log_File, maxBytes=250000, backupCount=5)
    except Exception as Error:
        log.fatal("Can't open logfile for writing: {} {}".format(globals.Log_File, Error) )
        exit(1)
 
    Log_Formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(module)s: %(message)s')
    Log_Console_Handler.setFormatter(Log_Formatter)
    Log_File_Handler.setFormatter(Log_Formatter)

    log.addHandler(Log_Console_Handler)
    log.addHandler(Log_File_Handler)
    return

#==================================================================================================
# Main function
#==================================================================================================
def main():
    #====================================================================================
    # Set paths & options from environment variables
    globals.Config_Path       = os.environ.get('CONFIG_PATH', "/config")
    globals.Default_Log_Lines = int( os.environ.get('DEFAULT_LOG_LINES', "20") )

    if os.environ.get('LOG_REQUESTS', "True").lower() == 'true':        
                                                globals.Log_Requests  = True
    else:                                       globals.Log_Requests  = False
    if os.environ.get('LOG_REQUESTS_DEBUG', "False").lower() == 'true': 
                                                globals.Log_Request_Debug = True
    else:                                       globals.Log_Request_Debug = False
    if os.environ.get('ORDER_METRICS', "True").lower() == 'true':       
                                                globals.Order_Metrics = True
    else:                                       globals.Order_Metrics = False

    #====================================================================================
    # Set up logging to a file and the console
    log = logging.getLogger()
    Configure_Log( log )
 
    #====================================================================================
    # Set some main values
    log.info("Program starting. App version is {}, Logging level is {}".format(
                        globals.App_Version, logging.getLevelName(logging.root.level)) )
    Server_Port = int(os.environ.get('PORT', '9995'))

    #====================================================================================
    # Load the configuration if given
    globals.Config = configuration.Load_Config()
    log.debug("Configuration in use:\n{}".format( globals.Config ))

    #====================================================================================
    # Launch the web browser
    http_server.Launch_HTTP_Server( Server_Port )

    return

#==================================================================================================
# Entry point
#==================================================================================================
if __name__ == '__main__':
    main()
