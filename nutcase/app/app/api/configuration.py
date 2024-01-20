import os
import yaml
from pathlib import PurePath

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
    if "log_level" in Config["settings"]:
        try:              
            app.logger.info("Setting log level: {}".format( Config["settings"]["log_level"].upper() ) )
            
#=======================================================================
#=======================================================================
#=======================================================================
#=======================================================================
# Beta override! TODO: Remove on release
#=======================================================================
#=======================================================================
#=======================================================================
#=======================================================================
            Debug_List = [ 'DEBUG', 'DEBUGV', 'DEBUGVV' ]
            if Config["settings"]["log_level"].upper() in Debug_List:
                app.logger.setLevel( Config["settings"]["log_level"].upper() )
            else:
                app.logger.setLevel( 'DEBUG' )
                app.logger.warning("Beta override: Config file logging level overridden")

        except Exception as Error: 
            app.logger.error("Error using log_level value from file: {}".format( Config["settings"]["log_level"] ) )

    #=======================================================================
    # Webhook settings
    #=======================================================================
    if "webhooks" in Config:
        app.config["WEBHOOKS"] = Config["webhooks"]

    #=======================================================================
    # Rework settings
    #=======================================================================
    if "rework" in Config:
        app.config["REWORK"] = Config["rework"]

    #=======================================================================
    # Servers & Credentials settings
    #=======================================================================
    if "servers" in Config:
        app.config["SERVERS"] = Config["servers"]
        if "credentials" in Config:
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
    if not os.path.isfile( app.config["CONFIG_FILENAME"] ):
        app.logger.warning("Config file missing {}".format( app.config["CONFIG_FILENAME"] ) )
        return False

    if os.path.getmtime(app.config["CONFIG_FILENAME"]) > app.config["CONFIG_MOD_TIME"]: 
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
    Sections          = [ 'credentials', 'rework', 'settings', 'webhooks', 'servers' ]
    Styles            = [ 'time', 'simple-enum', 'ratio', 'comp-enum', 'cl-count', 'cl-check' ]
    Expected_WebHooks = [ 'default', 'ok', 'fail' ]

    #=================================================================================
    # Check information is present
    #=================================================================================
    if not Config:
        app.logger.debug("Control file has no directives")
        return True

    if len( Config ) == 0:
        app.logger.debug("Control file has no directives (length = 0)")
        return True

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
    # if 'credentials' in Config:
    for Entry in Config['credentials']:
        try:
            assert 'server'   in Entry
            assert 'device'   in Entry
            assert 'username' in Entry
            assert 'password' in Entry
        except AssertionError:
            app.logger.error("Credentials need 'server', 'device', 'username' & 'password' {}".format(Entry))
            return False

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
                return True

    #=================================================================================
    # if 'rework' in Config:
    for Entry in Config['rework']:
        try:
            assert 'from'    in Entry
            assert 'to'      in Entry
            assert 'style'   in Entry
            assert 'control' in Entry
        except AssertionError:
            app.logger.error("Rework must have 'from', 'to', 'style' and 'control' entires {}".format(Entry))
            return False

        try:
            assert Entry['style'] in Styles
        except AssertionError:
            app.logger.error("Unknown style {}, styles are: {}".format( Entry,", ".join(Styles)))
            return False

        #================================================================================================
        if Entry['style'] == 'simple-enum' or Entry['style'] == 'comp-enum':
            try:
                assert 'from'    in Entry['control']
                assert 'to'      in Entry['control']
                assert 'default' in Entry['control']
                assert isinstance( Entry['control']['from'], list)
                assert isinstance( Entry['control']['to'], list)
                assert len( Entry['control']['from'] ) == len( Entry['control']['to'] )
            except AssertionError:
                app.logger.error("All enum style directives must have 'from', 'to' and 'default' in 'control' and 'from' and 'to' must be arrays of equal length\n{}".format( Entry ))
                return False
        #================================================================================================
        if Entry['style'] == 'cl-count':
            try:
                assert isinstance( Entry['control'], list )
                assert len(Entry['control']) == 4
                Entry['control'][0] = int( Entry['control'][0] ) 
            except AssertionError:
                app.logger.error("All cl-count style directives must have a 4 element array as the 'control' value with the first element being an integer.\n{}".format( Entry ))
                return False
        #================================================================================================
        if Entry['style'] == 'cl-check':
            try:
                assert isinstance( Entry['control'], list )
                assert len(Entry['control']) > 0
            except AssertionError:
                app.logger.error("All cl-check style directives must have a non-zero length array as the 'control' value.\n{}".format( Entry ))
                return False

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
# Load_Config
#====================================================================================================
def Load_Config( app ):
    #=================================================================================
    # Find the configuration file starting with .yml and changing to .yaml in needed
    # A user setting in the CONFIG_FILE overrides this.
    #=================================================================================
    Configfile_Dir  = os.path.join(app.root_path, app.config['LOGFILE_RELATIVE_PATH'])
    Config_Filename = os.path.join(Configfile_Dir, 'nutcase.yml')

    if not os.path.isfile( Config_Filename ):
        p = PurePath( Config_Filename )
        Check_Filename = p.with_suffix('.yaml')
        if os.path.isfile( Check_Filename ):
            Config_Filename = Check_Filename
            app.logger.debug("Changing config file to {}".format( Config_Filename ) )

    if not os.path.isfile( Config_Filename ):
        app.logger.info("Config file not found as either .yml or .yaml {}".format( Config_Filename ) )
        return None

    #=================================================================================
    # Load the YAML and convert to a dictionary
    #=================================================================================
    try:
        with open(Config_Filename, "r") as Config_File_Handle:
            try:
                Config = yaml.safe_load( Config_File_Handle )
                app.logger.info("Loaded YAML configuration from {}".format( Config_Filename ))
                app.logger.debug("Control YAML:\n{}".format( Config ))
                #=====================================================================
                # Record the mod time of the config file
                #=====================================================================
                app.config["CONFIG_MOD_TIME"] = os.path.getmtime( Config_Filename )
            except yaml.YAMLError as Error:
                app.logger.error("Error loading Control YAML {}".format( Error ))
                return None
    except Exception as Error:
        app.logger.warning("Could not open config file {}. Error: {}".format( Config_Filename, Error ) )
        return None

    app.config["CONFIG_FILENAME"] = Config_Filename

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
