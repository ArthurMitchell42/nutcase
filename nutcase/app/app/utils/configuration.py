import logging
import os
import yaml
from pathlib import PurePath

from app.utils import app_log_config

#====================================================================================================
# Load_YAML_As_Dictionary
#====================================================================================================
def Load_YAML_As_Dictionary( app, Filename ):
    #=================================================================================
    # Load the YAML and convert to a dictionary
    #=================================================================================
    try:
        with open(Filename, "r") as File_Handle:
            try:
                Data = yaml.safe_load( File_Handle )
                app.logger.debugv("Loaded YAML from {}".format( Filename ))
            except yaml.YAMLError as Error:
                app.logger.error("Error loading YAML {}".format( Error ))
                return None
    except Exception as Error:
        app.logger.warning("Could not open YAML file {}. Error: {}".format( Filename, Error ) )
        return None
    return Data

#====================================================================================================
# Save_Dictionary_As_YAML
#====================================================================================================
def Save_Dictionary_As_YAML( app, Filename, Data ):
    #=================================================================================
    # Save the dictionary as YAML
    #=================================================================================
    try:
        with open(Filename, "w") as File_Handle:
            try:
                yaml.dump( Data, File_Handle )
            except yaml.YAMLError as Error:
                app.logger.error("Error loading YAML {}".format( Error ))
                return False
    except Exception as Error:
        app.logger.warning("Could not save YAML file {}. Error: {}".format( Filename, Error ) )
        return False
    return True

#=======================================================================
# Get_Server - Return the server dictionary from Config->settings
#   or None
#=======================================================================
def Get_Server( app, Address ):
    Server = None
    for s in app.config['SERVERS']:
        if s['server'] == Address:
            Server = s
            break
    return Server

#=======================================================================
# Update_Settings - Implement the contents of Config->settings
#=======================================================================
def Update_Settings( Config, app ):
    #=======================================================================
    if "order_metrics" in Config["settings"]:
        if isinstance(Config["settings"]["order_metrics"], bool):
            app.config["ORDER_METRICS"] = Config["settings"]["order_metrics"]

    if "coloured_log" in Config["settings"]:
        if isinstance(Config["settings"]["coloured_log"], bool):
            app.config["COLOURED_LOG"] = Config["settings"]["coloured_log"]

    #=======================================================================
    if "default_log_lines" in Config["settings"]:
        if isinstance(Config["settings"]["default_log_lines"], int):
            app.config["DEFAULT_LOG_LINES"] = Config["settings"]["default_log_lines"]
    
    #=======================================================================
    if "cache_period" in Config["settings"]:
        if isinstance(Config["settings"]["cache_period"], int):
            app.config["CACHE_PERIOD"] = Config["settings"]["cache_period"]

    #=======================================================================
    if "apc_strip_units" in Config["settings"]:
        if isinstance(Config["settings"]["apc_strip_units"], bool):
            app.config["APC_STRIP_UNITS"] = Config["settings"]["apc_strip_units"]

    #=======================================================================
    if "ui_format_runtime" in Config["settings"]:
        app.config['UI']["FORMAT_RUNTIME"] = Config["settings"]["ui_format_runtime"]

    #=======================================================================
    # Log file settings
    #=======================================================================
    Update_RF_Handler = False
    if "log_maxbytes" in Config["settings"]:
        if isinstance(Config["settings"]["log_maxbytes"], int):
            app.config["LOGFILE_MAXBYTES"] = Config["settings"]["log_maxbytes"]
            Update_RF_Handler = True

    if "log_backupcount" in Config["settings"]:
        if isinstance(Config["settings"]["log_backupcount"], int):
            app.config["LOGFILE_BACKUPCOUNT"] = Config["settings"]["log_backupcount"]
            Update_RF_Handler = True

    if Update_RF_Handler:
        app_log_config.Update_RF_Handler( app )

    Console_Level = Logfile_Level = None
    if "log_level" in Config["settings"]:
        if app_log_config.Check_Level( Config["settings"]["log_level"].upper() ):
            Console_Level = Logfile_Level = Config["settings"]["log_level"].upper()

    if "log_level_console" in Config["settings"]:
        if app_log_config.Check_Level( Config["settings"]["log_level_console"].upper() ):
            Console_Level = Config["settings"]["log_level_console"].upper()

    if "log_level_logfile" in Config["settings"]:
        if app_log_config.Check_Level( Config["settings"]["log_level_logfile"].upper() ):
            Logfile_Level = Config["settings"]["log_level_logfile"].upper()

    if Console_Level:
        app_log_config.Set_Log_Level( app, Console_Level, "con" )
        app.logger.info("Setting console log level from config {}".format( Console_Level ) )

    if Logfile_Level:
        app_log_config.Set_Log_Level( app, Logfile_Level, "rfh" )
        app.logger.info("Setting logfile log level from config {}".format( Logfile_Level ) )

    #=======================================================================
    # As a beta testing measure only, the log level can be overridden
    #=======================================================================
    if app.config["BETA_OVERRIDE"]:
        Console_Handler = app_log_config.Get_Handler( app, 'con' )
        if 'DEBUG' not in logging.getLevelName(Console_Handler):
            Console_Handler.setLevel( 'DEBUG' )
            app.logger.warning("Beta override: Console logging level overridden to DEBUG. (Sorry about the file size)")

        Logfile_Handler = app_log_config.Get_Handler( app, 'rfh' )
        if 'DEBUG' not in logging.getLevelName(Logfile_Handler):
            Logfile_Handler.setLevel( 'DEBUG' )
            app.logger.warning("Beta override: Logfile logging level overridden to DEBUG. (Sorry about the file size)")

    #=======================================================================
    # Webhook settings
    #=======================================================================
    if "webhooks" in Config:
        # app.config["WEBHOOKS"] = Config["webhooks"]
        app.config.update( WEBHOOKS = Config["webhooks"] )

    #=======================================================================
    # Rework settings
    #=======================================================================
    if "rework" in Config:
        # app.config["REWORK"] = Config["rework"]
        app.config.update( REWORK = Config["rework"] )

    #=======================================================================
    # Servers & Credentials settings
    #=======================================================================
    if "servers" in Config:
        app.config["SERVERS"] = Config["servers"]
        # if "credentials" in Config:
        for Srv in app.config["SERVERS"]:
            if 'username' in Srv and 'password' in Srv:
                app.config["CREDENTIALS"].append( {
                    'server': Srv['server'],
                    'device': Srv['device'],
                    'username': Srv['username'],
                    'password': Srv['password']
                } )
    return

#=======================================================================
# Config_File_Modified
#=======================================================================
def Config_File_Modified( app ):
    if not os.path.isfile( app.config["CONFIG_FULLNAME"] ):
        app.logger.warning("Config file missing {}".format( app.config["CONFIG_FULLNAME"] ) )
        return False

    if os.path.getmtime(app.config["CONFIG_FULLNAME"]) > app.config["CONFIG_MOD_TIME"]: 
        app.logger.debug("Config file has been updated" )
        return True
    return False

#====================================================================================================
# Check and add variables that are requested to be reworks to a list in the reworks dictionary
#   This speeds up parsing after a scrape by making a quick lookup table of vaiable names.
#====================================================================================================
def List_Variables( Config, app ):
    Var_List = []
    for Rework in Config['rework']:
        if Rework["from"] not in Var_List:
            Var_List.append( Rework["from"] )

    app.config["REWORK_VAR_LIST"] = Var_List
    return

#====================================================================================================
# Load_Config
#   Returns:
#       True  : Config passes tests
#       False : Config failed tests
#====================================================================================================
def Parse_Config( Config, app ):
    Sections          = [ 'rework', 'settings', 'webhooks', 'servers' ]
    Styles            = [ 'time', 'simple-enum', 'ratio', 'comp-enum', 'cl-count', 'cl-check' ]
    Expected_WebHooks = [ 'default', 'ok', 'fail' ]

    #=================================================================================
    # Check information is present
    #=================================================================================
    if not Config or len( Config ) == 0:
        app.logger.debug("Control file has no directives")
        return False

    #=================================================================================
    # All Sections entries should always be in the Config dictionary, even if empty
    #=================================================================================
    for Expected_Section in Sections:
        if Expected_Section not in Config: Config[Expected_Section] = {}
        if not Config[Expected_Section]:   Config[Expected_Section] = {}

    #=================================================================================
    for Section in Config:
        try:
            assert Section in Sections
        except AssertionError:
            app.logger.warning("Unknown section type {}".format( Section ))

    #=================================================================================
    # Check all required fields are present
    #=================================================================================

    #=================================================================================
    # if 'webhooks' in Config:
    for Hook_Name in Config['webhooks']:
        try:
            assert Hook_Name in Expected_WebHooks
        except AssertionError:
            app.logger.warning("Unknown WebHook name {}. Expected names: {}".format( 
                Hook_Name,
                ",".join(Expected_WebHooks) ))

    if 'default' not in Config['webhooks']:
        for Expected_Name in Expected_WebHooks:
            try:
                assert Expected_Name in Config['webhooks']
            except AssertionError:
                app.logger.warning("Config is missing WebHook name {}".format( Expected_Name ))

    #=================================================================================
    # if 'rework' in Config:
    Checked_Rework = []
    for Entry in Config['rework']:
        Include_Directive = True
        try:
            assert 'from'    in Entry
            assert 'to'      in Entry
            assert 'style'   in Entry
            assert 'control' in Entry
        except AssertionError:
            app.logger.error("All rework directives must have 'from', 'to', 'style' and 'control' entires {}".format(Entry))
            Include_Directive = False

        try:
            assert Entry['style'] in Styles
        except AssertionError:
            app.logger.error("Unknown style {}, styles are: {}".format( Entry,", ".join(Styles)))
            Include_Directive = False

        #================================================================================================
        if Include_Directive and Entry['style'] == 'simple-enum' or Entry['style'] == 'comp-enum':
            try:
                assert isinstance( Entry['control'], dict)
            except AssertionError:
                app.logger.error("For simple-enum style 'control' must be a dictionary, not a list etc. Found:\n{}".format( Entry['control'] ))
                Include_Directive = False

            try:
                assert 'from'    in Entry['control']
                assert 'to'      in Entry['control']
                assert 'default' in Entry['control']
                assert isinstance( Entry['control']['from'], list)
                assert isinstance( Entry['control']['to'], list)
                assert len( Entry['control']['from'] ) == len( Entry['control']['to'] )
            except AssertionError:
                app.logger.error("All enum style directives must have 'from', 'to' and 'default' in 'control' and 'from' and 'to' must be arrays of equal length\n{}".format( Entry ))
                Include_Directive = False
        #================================================================================================
        elif Include_Directive and Entry['style'] == 'cl-count':
            try:
                assert isinstance( Entry['control'], list )
                assert len(Entry['control']) == 4
                Entry['control'][0] = int( Entry['control'][0] ) 
            except AssertionError:
                app.logger.error("All cl-count style directives must have a 4 element array as the 'control' value with the first element being an integer.\n{}".format( Entry ))
                Include_Directive = False
        #================================================================================================
        elif Include_Directive and Entry['style'] == 'cl-check':
            try:
                assert isinstance( Entry['control'], list )
                assert len(Entry['control']) > 0
            except AssertionError:
                app.logger.error("All cl-check style directives must have a non-zero length array as the 'control' value.\n{}".format( Entry ))
                Include_Directive = False

        if Include_Directive:
            Checked_Rework.append(Entry)
    
    Config['rework'] = Checked_Rework

    #=================================================================================
    # if 'servers' in Config:
    for Entry in Config['servers']:
        try:
            assert 'server'  in Entry
            assert 'port'    in Entry
            assert 'device'  in Entry
        except AssertionError:
            app.logger.error("Server entries must have 'server', 'port' and 'device' entires {}".format(Entry))
            return False

    return True

#====================================================================================================
# Identify_Config_File
#====================================================================================================
def Identify_Config_File( app ):
    #=================================================================================
    # Find the configuration file starting with .yml and changing to .yaml in needed
    # A user setting in the CONFIG_FILE overrides this.
    #=================================================================================
    app.logger.debugv("Load_Config: CONFIG_PATH {} CONFIG_FILE {}".format( app.config['CONFIG_PATH'], app.config['CONFIG_FILE'] ) )
    Config_Filename = os.path.join(app.config['CONFIG_PATH'], app.config['CONFIG_FILE'])

    p = PurePath( Config_Filename )
    Check_Filename = p.with_suffix('.yml')

    app.logger.debugv("Load_Config: Trying Check_Filename {}".format( Check_Filename ) )

    if not os.path.isfile( Check_Filename ):
        Check_Filename = p.with_suffix('.yaml')
        app.logger.debugv("Load_Config: Not found, Trying Check_Filename {}".format( Check_Filename ) )
        if not os.path.isfile( Check_Filename ):
            app.logger.warning("Config file not found as either .yml or .yaml {}".format( app.config['CONFIG_FILE'] ) )
            return None
        
    app.logger.debug("Config file is {}".format( Check_Filename ) )
    app.config.update( CONFIG_FULLNAME = Check_Filename )
    return Check_Filename

#====================================================================================================
# Load_Config
#====================================================================================================
def Load_Config( app ):
    #=================================================================================
    # Put the identified config file name in CONFIG_FULLNAME
    #=================================================================================
    Config_Filename = Identify_Config_File( app )

    #=================================================================================
    # Load the YAML and convert to a dictionary
    #=================================================================================
    Config = Load_YAML_As_Dictionary( app, Config_Filename )

    #=====================================================================
    # Record the mod time of the config file
    #=====================================================================
    if Config_Filename and os.path.isfile( Config_Filename ):
        app.config.update( CONFIG_MOD_TIME = os.path.getmtime( Config_Filename ) )
    
    #=================================================================================
    # Do validity checking in the loaded configuration
    #=================================================================================
    if not Parse_Config( Config, app ):
        app.logger.error("Config file has issues, file ignored {}".format( Config_Filename ) )
        return None

    #=================================================================================
    # Act on settings
    #=================================================================================
    Update_Settings( Config, app )

    #=================================================================================
    # Prepare a list of variables to be reworked in the dictionary
    #   This LUT speeds up parsing after a scrape.
    #=================================================================================
    if Config:
        List_Variables( Config, app )
    
    app.logger.debugv("Config in use:\n{}".format( Config ) )
    app.logger.debugv("ORDER_METRICS: {}".format(  app.config["ORDER_METRICS"] ) )
    app.logger.debugv("COLOURED_LOG: {}".format(  app.config["COLOURED_LOG"] ) )
    app.logger.debugv("DEFAULT_LOG_LINES: {}".format(  app.config["DEFAULT_LOG_LINES"] ) )
    app.logger.debugv("CACHE_PERIOD: {}".format(  app.config["CACHE_PERIOD"] ) )
    app.logger.debugv("WEBHOOKS: {}".format(  app.config["WEBHOOKS"] ) )
    app.logger.debugv("REWORK_VAR_LIST: {}".format(  app.config["REWORK_VAR_LIST"] ) )
    app.logger.debugv("CREDENTIALS: {}".format(  app.config["CREDENTIALS"] ) )
    app.logger.debugv("REWORK: {}".format(  app.config["REWORK"] ) )

    return Config
