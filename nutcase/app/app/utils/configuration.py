import logging
import os
import yaml
from pathlib import PurePath
from flask import current_app
from app.utils import app_log_config

# ===================================================================================================
# region Load & Save YAML
# Load_YAML_As_Dictionary
# ===================================================================================================
def Load_YAML_As_Dictionary(app, Filename):
    # ================================================================================
    # Load the YAML and convert to a dictionary
    # ================================================================================
    try:
        with open(Filename, "r") as File_Handle:
            try:
                Data = yaml.safe_load(File_Handle)
                app.logger.info("Loaded YAML from {}".format(Filename))
            except yaml.YAMLError as Error:
                app.logger.error("Error loading YAML {}".format(Error))
                return None
    except Exception as Error:
        app.logger.warning("Could not open YAML file {}. Error: {}".format(Filename, Error))
        return None
    return Data

# ===================================================================================================
# Save_Dictionary_As_YAML
# ===================================================================================================
def Save_Dictionary_As_YAML(app, Filename, Data):
    # ================================================================================
    # Save the dictionary as YAML
    # ================================================================================
    try:
        with open(Filename, "w") as File_Handle:
            try:
                yaml.dump(Data, File_Handle)
            except yaml.YAMLError as Error:
                app.logger.error("Error loading YAML {}".format(Error))
                return False
    except Exception as Error:
        app.logger.warning("Could not save YAML file {}. Error: {}".format(Filename, Error))
        return False
    return True

# ======================================================================
# region Utils
# Get_Server - Return the server dictionary from Config->settings
#   or None
# ======================================================================
def Get_Server(Address):
    Server = None
    for s in current_app.config['SERVERS']:
        if s['server'] == Address:
            Server = s
            break
    return Server

# ======================================================================
# Get_Server - Return the server dictionary from Config->settings
#   or None
# ======================================================================
def Get_Device(Server_Address, Device_Name):
    Device = None
    Server = Get_Server(Server_Address)

    if Server:
        if 'devices' in Server:
            for dev in Server['devices']:
                if dev['device'] == Device_Name:
                    Device = dev
                    break
    return Device

# ======================================================================
# region Update_Settings
# Implement the contents of Config->settings
# ======================================================================
def Update_Settings(Config):
    # ======================================================================
    if "order_metrics" in Config["settings"]:
        if isinstance(Config["settings"]["order_metrics"], bool):
            current_app.config["ORDER_METRICS"] = Config["settings"]["order_metrics"]

    if "coloured_log" in Config["settings"]:
        if isinstance(Config["settings"]["coloured_log"], bool):
            current_app.config["COLOURED_LOG"] = Config["settings"]["coloured_log"]

    # ======================================================================
    if "default_log_lines" in Config["settings"]:
        if isinstance(Config["settings"]["default_log_lines"], int):
            current_app.config["DEFAULT_LOG_LINES"] = Config["settings"]["default_log_lines"]

    # ======================================================================
    if "cache_period" in Config["settings"]:
        if isinstance(Config["settings"]["cache_period"], int):
            current_app.config["CACHE_PERIOD"] = Config["settings"]["cache_period"]

    # ======================================================================
    if "apc_strip_units" in Config["settings"]:
        if isinstance(Config["settings"]["apc_strip_units"], bool):
            current_app.config["APC_STRIP_UNITS"] = Config["settings"]["apc_strip_units"]

    # ======================================================================
    if "ui_format_runtime" in Config["settings"]:
        current_app.config['UI']["FORMAT_RUNTIME"] = Config["settings"]["ui_format_runtime"]

    # ======================================================================
    # Log file settings
    # ======================================================================
    Update_RF_Handler = False
    if "log_maxbytes" in Config["settings"]:
        if isinstance(Config["settings"]["log_maxbytes"], int):
            current_app.config["LOGFILE_MAXBYTES"] = Config["settings"]["log_maxbytes"]
            Update_RF_Handler = True

    if "log_backupcount" in Config["settings"]:
        if isinstance(Config["settings"]["log_backupcount"], int):
            current_app.config["LOGFILE_BACKUPCOUNT"] = Config["settings"]["log_backupcount"]
            Update_RF_Handler = True

    if Update_RF_Handler:
        app_log_config.Update_RF_Handler(current_app)

    Console_Level = Logfile_Level = None
    if "log_level" in Config["settings"]:
        if app_log_config.Check_Level( Config["settings"]["log_level"].upper()):
            Console_Level = Logfile_Level = Config["settings"]["log_level"].upper()

    if "log_level_console" in Config["settings"]:
        if app_log_config.Check_Level( Config["settings"]["log_level_console"].upper()):
            Console_Level = Config["settings"]["log_level_console"].upper()

    if "log_level_logfile" in Config["settings"]:
        if app_log_config.Check_Level( Config["settings"]["log_level_logfile"].upper()):
            Logfile_Level = Config["settings"]["log_level_logfile"].upper()

    if Console_Level:
        app_log_config.Set_Log_Level( current_app, Console_Level, "con")

    if Logfile_Level:
        app_log_config.Set_Log_Level( current_app, Logfile_Level, "rfh")

    # ======================================================================
    # As a beta testing measure only, the log level can be overridden
    # ======================================================================
    if current_app.config["BETA_OVERRIDE"]:
        Console_Handler = app_log_config.Get_Handler( current_app, 'con')
        if 'DEBUG' not in logging.getLevelName(Console_Handler):
            Console_Handler.setLevel( 'DEBUG')
            current_app.logger.warning("Beta override: Console logging level overridden to DEBUG.")

        Logfile_Handler = app_log_config.Get_Handler( current_app, 'rfh')
        if 'DEBUG' not in logging.getLevelName(Logfile_Handler):
            Logfile_Handler.setLevel( 'DEBUG')
            current_app.logger.warning("Beta override: Logfile logging level overridden to DEBUG.")

    # ======================================================================
    # Webhook settings
    # ======================================================================
    if "webhooks" in Config:
        current_app.config.update( WEBHOOKS = Config["webhooks"])

    # ======================================================================
    # Rework settings
    # ======================================================================
    if "rework" in Config:
        current_app.config.update( REWORK = Config["rework"])

    # ======================================================================
    # Servers & Credentials settings
    # ======================================================================
    if "servers" in Config:
        current_app.config["SERVERS"] = Config["servers"]

        for Srv in current_app.config["SERVERS"]:
            if 'mode' not in Srv:
                Srv['mode'] = 'nut'

            if 'username' in Srv and 'password' in Srv:
                current_app.config["CREDENTIALS"].append( {
                    'server': Srv['server'],
                    'device': Srv['device'],
                    'username': Srv['username'],
                    'password': Srv['password']
                })
    return

# ======================================================================
# Config_File_Modified
# ======================================================================
def Config_File_Modified():
    if not os.path.isfile( current_app.config["CONFIG_FULLNAME"]):
        current_app.logger.warning("Config file missing {}".format(
                                current_app.config["CONFIG_FULLNAME"]))
        return False

    if os.path.getmtime(current_app.config["CONFIG_FULLNAME"]) > \
                current_app.config["CONFIG_MOD_TIME"]:
        current_app.logger.info("Config file has been updated")
        return True
    return False

# =============================================================================================
# Check and add variables that are requested to be reworks to a list in the reworks dictionary
#   This speeds up parsing after a scrape by making a quick lookup table of vaiable names.
# =============================================================================================
def List_Variables(Config):
    Var_List = []
    for Rework in Config['rework']:
        if "from" in Rework:
            if Rework["from"] not in Var_List:
                Var_List.append( Rework["from"])

    current_app.config["REWORK_VAR_LIST"] = Var_List
    return

# =============================================================================================
# region Parse_Config
#   Returns:
#       True  : Config passes tests
#       False : Config failed tests
# =============================================================================================
def Parse_Config(Config):
    Sections          = ['rework', 'settings', 'webhooks', 'servers']
    Styles            = ['time', 'simple-enum', 'ratio', 'comp-enum', 'cl-count',
                         'cl-check', 'nutcase_logs']
    Expected_WebHooks = ['ok', 'fail']

    # ================================================================================
    # All Sections entries should always be in the Config dictionary, even if empty
    # ================================================================================
    for Expected_Section in Sections:
        if Expected_Section not in Config:
            if Expected_Section == 'servers' or Expected_Section == 'rework':
                Config[Expected_Section] = []
            else:
                Config[Expected_Section] = {}
        if not Config[Expected_Section]:
            if Expected_Section == 'servers' or Expected_Section == 'rework':
                Config[Expected_Section] = []
            else:
                Config[Expected_Section] = {}

    # ================================================================================
    for Section in Config:
        if Section not in Sections:
            current_app.config.update(CONFIG_ERROR = True)
            current_app.logger.warning("Unknown section type {}".format( Section))

    # ================================================================================
    # Check 'webhooks'
    # ================================================================================
    for Hook_Name in Config['webhooks']:
        try:
            if Hook_Name != 'default':
                assert Hook_Name in Expected_WebHooks
        except AssertionError:
            current_app.config.update(CONFIG_ERROR = True)
            current_app.logger.warning("Unknown WebHook name {}. Expected names: {}".format(
                Hook_Name,
                ",".join(Expected_WebHooks)))

    if 'default' not in Config['webhooks']:
        for Expected_Name in Expected_WebHooks:
            try:
                assert Expected_Name in Config['webhooks']
            except AssertionError:
                current_app.logger.warning("Config is missing WebHook name {}".format(
                                                                        Expected_Name))

    # ================================================================================
    # Check 'rework'
    # ================================================================================
    Checked_Rework = []
    for Entry in Config['rework']:
        try:
            assert 'to' in Entry
            assert 'style' in Entry
            assert 'control' in Entry
            if Entry['style'] != "nutcase_logs":
                assert 'from' in Entry

            try:
                assert Entry['style'] in Styles
            except AssertionError:
                current_app.logger.error("Unknown style {}, styles are: {}".format( Entry,
                                                                            ", ".join(Styles)))
                continue

            # =====================================================================================
            if Entry['style'] == 'simple-enum' or Entry['style'] == 'comp-enum':
                try:
                    assert isinstance( Entry['control'], dict)
                except AssertionError:
                    current_app.logger.error(
                        "simple-enum control must be dictionary Found: {}".format(Entry['control']))
                    continue

                try:
                    assert 'from' in Entry['control']
                    assert 'to' in Entry['control']
                    assert 'default' in Entry['control']
                    assert isinstance( Entry['control']['from'], list)
                    assert isinstance( Entry['control']['to'], list)
                    assert len( Entry['control']['from']) == len( Entry['control']['to'])
                except AssertionError:
                    current_app.logger.error(
                        "enum control needs from to & default, from & to equal len")
                    continue
            # =========================================================================================
            elif Entry['style'] == 'cl-count':
                try:
                    assert isinstance( Entry['control'], list)
                    assert len(Entry['control']) == 4
                    if isinstance(Entry['control'][0], str):
                        if Entry['control'][0] == 'auto':
                            assert True
                        elif Entry['control'][0].isnumeric():
                            assert True
                        else:
                            assert False
                    elif isinstance(Entry['control'][0], int):
                        assert True
                    else:
                        assert False
                except Exception:
                    current_app.logger.error(
                        "cl-count control=4 el. array, elem0 must be int")
                    continue
            # =========================================================================================
            elif Entry['style'] == 'cl-check':
                try:
                    if isinstance( Entry['control'], list):
                        assert len(Entry['control']) > 0
                    elif isinstance( Entry['control'], str):
                        assert Entry['control'] == "auto"
                    else:
                        assert False
                except AssertionError:
                    current_app.logger.error(
                        "cl-check must have a non-zero length array for 'control'")
                    continue
            # =========================================================================================
            elif Entry['style'] == 'nutcase_logs':
                try:
                    assert isinstance( Entry['control'], str)
                except AssertionError:
                    current_app.logger.error(
                        "nutcase_logs must have a string for 'control'")
                    continue

            Checked_Rework.append(Entry)
        except AssertionError:
            current_app.logger.error("All rework's must have from to style & control")

    Config['rework'] = Checked_Rework

    # ================================================================================
    # Check 'servers'
    # ================================================================================
    for Entry in Config['servers']:
        try:
            assert 'server' in Entry
            assert 'port' in Entry
            assert 'devices' in Entry
            assert isinstance( Entry['devices'], list)
            assert len(Entry['devices']) > 0
        except AssertionError:
            current_app.logger.error(
                "Server entries must have 'server', 'port' and at least one entry "
                "in the 'devices' list")
            return False

    return True

# ===================================================================================================
# Identify_Config_File
# ===================================================================================================
def Identify_Config_File():
    # ================================================================================
    # Find the configuration file starting with .yml and changing to .yaml in needed
    # A user setting in the CONFIG_FILE overrides this.
    # ================================================================================
    Config_Filename = os.path.join(current_app.config['CONFIG_PATH'],
                                   current_app.config['CONFIG_FILE'])

    p = PurePath(Config_Filename)
    Check_Filename = p.with_suffix('.yml')

    if not os.path.isfile(Check_Filename):
        Check_Filename = p.with_suffix('.yaml')
        if not os.path.isfile(Check_Filename):
            current_app.logger.warning("Config file ({}) not found as either .yml or .yaml".format(
                                current_app.config['CONFIG_FILE']))
            return None

    current_app.logger.info("Config file is {}".format( Check_Filename))
    current_app.config.update( CONFIG_FULLNAME = Check_Filename)
    return Check_Filename

# ===================================================================================================
# region Load_Config
# ===================================================================================================
def Load_Config():
    # ================================================================================
    # Put the identified config file name in CONFIG_FULLNAME
    # ================================================================================
    Config_Filename = Identify_Config_File()
    if not Config_Filename:
        current_app.config.update(CONFIG_ERROR = True)
        current_app.logger.warning("Couldn't identify config file {}".format( Config_Filename))
        return None

    # ================================================================================
    # Load the YAML and convert to a dictionary
    # ================================================================================
    Config = Load_YAML_As_Dictionary(current_app, Config_Filename)
    if not Config:
        current_app.config.update(CONFIG_ERROR = True)
        current_app.logger.warning("Couldn't load YAML {}".format( Config_Filename))
        return None

    # ====================================================================
    # Record the mod time of the config file
    # ====================================================================
    current_app.config.update(CONFIG_MOD_TIME = os.path.getmtime(Config_Filename))

    # ================================================================================
    # Do validity checking in the loaded configuration
    # ================================================================================
    if not Parse_Config(Config):
        current_app.logger.error("Config file has issues, file ignored {}".format(Config_Filename))
        current_app.config.update(CONFIG_ERROR = True)
        return None

    # ================================================================================
    # Act on settings
    # ================================================================================
    Update_Settings(Config)

    # ================================================================================
    # Prepare a list of variables to be reworked in the dictionary
    #   This LUT speeds up parsing after a scrape.
    # ================================================================================
    if Config:
        List_Variables(Config)

    current_app.logger.debugv("Config in use:\n{}".format(Config))
    current_app.logger.debugv("WEBHOOKS: {}".format(current_app.config["WEBHOOKS"]))
    current_app.logger.debugv("REWORK_VAR_LIST: {}".format(current_app.config["REWORK_VAR_LIST"]))
    current_app.logger.debugv("REWORK: {}".format(current_app.config["REWORK"]))

    return Config
