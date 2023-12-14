import logging
import os
import yaml

import globals

#=======================================================================
# Connect to the app log
#=======================================================================
log = logging.getLogger('__main__.' + __name__)

#====================================================================================================
# Check and add variables that are requested to be reworks to a list in the reworks dictionary
#   This speeds up parsing after a scrape by making a quick lookup table of vaiable names.
#====================================================================================================
def List_Variables( Config ):
    Var_List = []
    for Rework in Config['rework']:
        if Rework["from"] not in Var_List:
            Var_List.append( Rework["from"] )

    Config["rework_var_list"] = Var_List
    return

#====================================================================================================
# Load_Config
#   Returns:
#       True  : Config passes tests
#       False : Config failed tests
#====================================================================================================
def Parse_Config( Config ):
    Sections = [ 'credentials', 'rework' ]
    Styles = [ 'time', 'simple-enum', 'ratio', "comp-enum" ]

    #=================================================================================
    # Check information is present
    #=================================================================================
    if not Config:
        log.debug("Control file has no directives")
        return True

    if len( Config ) == 0:
        log.debug("Control file has no directives length = 0")
        return True

    for Section in Config:
        try:
            assert Section in Sections
            # log.debug("Section {} found".format( Section ) )
        except AssertionError:
            log.error("Unknown section type {}".format( Section ))
            return False

    #=================================================================================
    # Check all required fields are present
    #=================================================================================
    if 'credentials' in Config:
        # log.debug("Checking {} credential(s)".format( len(Config['credentials']) ) )
        for Entry in Config['credentials']:
            try:
                assert 'device'   in Entry
                assert 'username' in Entry
                assert 'password' in Entry
            except AssertionError:
                log.error("All credentials must have 'device', 'username' and 'password' {}".format( Entry ))
                return False

    if 'rework' in Config:
        # log.debug("Checking {} rework(s)".format( len(Config['rework']) ) )
        for Entry in Config['rework']:
            try:
                assert 'from'    in Entry
                assert 'to'      in Entry
                assert 'style'   in Entry
                assert 'control' in Entry
            except AssertionError:
                log.error("All rework actions must have 'from', 'to', 'style' and 'control' {}".format( Entry ))
                return False

            try:
                assert Entry['style'] in Styles
            except AssertionError:
                log.error("Unknown 'style' {}, known styles are: {}".format( Entry, ", ".join( Styles ) ))
                return False

            if Entry['style'] == 'simple-enum' or Entry['style'] == 'comp-enum':
                try:
                    assert 'from'    in Entry['control']
                    assert 'to'      in Entry['control']
                    assert 'default' in Entry['control']
                    assert isinstance( Entry['control']['from'], list)
                    assert isinstance( Entry['control']['to'], list)
                    assert len( Entry['control']['from'] ) == len( Entry['control']['to'] )
                except AssertionError:
                    log.error("All enum style directives must have 'from', 'to' and 'default' in 'control' and 'from' and 'to' must be arrays of equal length\n{}".format( Entry ))
                    return False
    return True

#====================================================================================================
# Load_Config
#====================================================================================================
def Load_Config():
    #=================================================================================
    # Find the configuration file, if present
    #=================================================================================
    Config_Filename = os.environ.get('CONFIG_FILE', "nutcase.yml")
    Config_File = os.path.join(globals.Config_Path, Config_Filename)

    if not os.path.isfile( Config_File ):
        log.debug("Config file not found {}".format( Config_File ) )
        return None

    #=================================================================================
    # Load the YAML and convert to a dictionary
    #=================================================================================
    try:
        with open(Config_File, "r") as Config_File_Handle:
            try:
                Config = yaml.safe_load( Config_File_Handle )
                log.info("Loaded Control_YAML from {}".format( Config_File ))
                log.debug("Control_YAML:\n{}".format( Config ))
            except yaml.YAMLError as Error:
                log.error("Error loading Control_YAML {}".format( Error ))
                return None
    except Exception as Error:
        log.warning("Could not open config file {}. Error: {}".format( Config_File, Error ) )
        return None

    #=================================================================================
    # Do validity checking in the loaded configuration
    #=================================================================================
    if not Parse_Config( Config ):
        log.error("Config file has issues, file ignored {}".format( Config_File ) )
        return None

    #=================================================================================
    # Prepare a list of variables to be reworked in the dictionary
    #   This LUT speeds up parsing after a scrape.
    #=================================================================================
    if Config:
        List_Variables( Config )
    
    return Config
