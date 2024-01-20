from flask import current_app

import time         # To format time variables 
import re           # for splitting status strings

from app.api import format_to_text
from app.api import configuration

#====================================================================================================
# Transform a variable to an enumerated string
#====================================================================================================
def Transform_Simple_Enum( Var, Rework ):
    New_Var = {"name": Rework["to"], "value": ""}

    Search_String = Var["value"]
    current_app.logger.debugv("SimpEnum: Looking for {} in {}".format( Search_String, Rework["control"]["from"] )) 

    if Search_String in Rework["control"]["from"]:
        Index = Rework["control"]["from"].index( Search_String )
        New_Value = Rework["control"]["to"][Index]
    else:
        New_Value = Rework["control"]["default"]

    New_Var["value"] = New_Value
    return New_Var 

#====================================================================================================
# Transform a variable to an enumerated string
#====================================================================================================
def Transform_Composite_Enum( Var, Rework ):
    New_Var = {"name": Rework["to"], "value": ""}
    Found_Match = False

    if 'join' in Rework["control"]:
        Join = Rework["control"]["join"]
    else:
        Join = " "

    Search_List = re.split(r' |:|;|-|\.|/|\\', Var["value"])
    current_app.logger.debugv("CompEnum: Looking for {} in {}".format( Search_List, Rework["control"]["from"] )) 

    Comp_Value = ""
    for Search_String in Search_List:
        if Search_String in Rework["control"]["from"]:
            Index = Rework["control"]["from"].index( Search_String )
            if len(Comp_Value) == 0:
                Comp_Value = Rework["control"]["to"][Index]
            else:
                Comp_Value += Join + Rework["control"]["to"][Index]
            Found_Match = True

    if not Found_Match:
        Comp_Value = Rework["control"]["default"]

    New_Var["value"] = Comp_Value
    return New_Var 

#====================================================================================================
# Transform a variable to a ratio
#====================================================================================================
def Transform_Ratio( Var, Rework, UPS ):
    New_Var = {"name": Rework["to"], "value": ""}

    if Nominal_Power := format_to_text.Get_NUT_Variable( UPS, Rework["control"] ):
        Nominal_Power = int( float(Nominal_Power) )
    else:
        Nominal_Power = 0

    if Server := configuration.Get_Server( current_app, UPS['server_address'] ):
        if 'power' in Server:
            Nominal_Power = Server['power']
            current_app.logger.debug("Using power value from config {}".format( Nominal_Power ))

    Percent_Power = float( Var["value"] )

    Ratio = Nominal_Power * (Percent_Power/100)
    New_Var["value"] = str( round(Ratio, 1) )
    return New_Var 

#====================================================================================================
# Transform a variable to a time string
#====================================================================================================
def Transform_Time( Var, Rework ):
    New_Var = {"name": Rework["to"], "value": ""}
    formatted_time = time.strftime(Rework["control"], time.gmtime( int(Var["value"]) ))
    New_Var["value"] = formatted_time
    return New_Var 

#====================================================================================================
# Parse data and add transformed variables
#====================================================================================================
def Transform_Variable( Var, Rework, UPS ):
    current_app.logger.debugv("Transforming: {} with transform {} and appending to UPS {}".format( Var["name"], Rework["style"], UPS["name"] ))    

    if Rework["style"].lower() == "time":
        New_Var = Transform_Time(Var, Rework )
        if New_Var:
            UPS["variables"].append( New_Var )
    elif Rework["style"].lower() == "ratio":
        New_Var = Transform_Ratio(Var, Rework, UPS )
        if New_Var:
            UPS["variables"].append( New_Var )
    elif Rework["style"].lower() == "simple-enum":
        New_Var = Transform_Simple_Enum(Var, Rework )
        if New_Var:
            UPS["variables"].append( New_Var )
    elif Rework["style"].lower() == "comp-enum":
        New_Var = Transform_Composite_Enum(Var, Rework )
        if New_Var:
            UPS["variables"].append( New_Var )
    else:
        current_app.logger.debug("Unknown transform string {}".format( Rework["style"] ))
    return

#====================================================================================================
# 
#====================================================================================================
def Transform_Client_Count(UPS, Rework ):
    current_app.logger.debugv("Applying transform {} and appending to UPS {}".format( Rework["style"], UPS["name"] ))    
    
    New_Var = {"name": Rework["to"], "value": ""}

    Expected = int( Rework["control"][0] )
    diff = abs( len( UPS["clients"] ) - Expected )

    if diff == 0:
        Display = Rework["control"][2].format( d=diff, c=Expected )
    elif diff > 0:
        Display = Rework["control"][3].format( d=diff, c=Expected )
    elif diff < 0:
        Display = Rework["control"][1].format( d=diff, c=Expected )

    New_Var["value"] = Display
    return New_Var

#====================================================================================================
# 
#====================================================================================================
def Transform_Client_Check(UPS, Rework ):
    current_app.logger.debugv("Applying transform {} and appending to UPS {}".format( Rework["style"], UPS["name"] ))    

    New_Var = {"name": Rework["to"], "value": ""}

    Missing = []
    for a in Rework["control"]:
        if a not in UPS['clients']:
            Missing.append( a )

    if len(Missing) > 0:
        Display = "Missing {} ({})".format( len(Missing), Missing[0] )
    else:
        Display = "All present"

    New_Var["value"] = Display
    return New_Var

#====================================================================================================
# 
#====================================================================================================
def Transform_Clients( Rework, UPS ):
    current_app.logger.debug("Transforming: clients of {} with transform {}".format( UPS["name"], Rework["style"] ))    

    if Rework["style"].lower() == "cl-count":
        New_Var = Transform_Client_Count(UPS, Rework )
        if New_Var:
            UPS["variables"].append( New_Var )
    elif Rework["style"].lower() == "cl-check":
        New_Var = Transform_Client_Check(UPS, Rework )
        if New_Var:
            UPS["variables"].append( New_Var )
    return

#====================================================================================================
# Parse data and add transformed variables
#====================================================================================================
def Rework_Variables( Scrape_Data ):
    for ups in Scrape_Data["ups_list"]:                             # Loop through the UPS devices
        for var in ups["variables"]:                                # Loop through each variable for this UPS
            if var["name"] in current_app.config["REWORK_VAR_LIST"]:# Is the variable in the list of ones to transform?
                for Rework in current_app.config["REWORK"]:         # Loop through the transforms in the control file
                    if Rework["from"] == var["name"]:
                        Transform_Variable( var, Rework, ups )

        if ups["name"] in current_app.config["REWORK_VAR_LIST"]:
            for Rework in current_app.config["REWORK"]:             # Loop through the transforms in the control file
                if Rework["from"] == ups["name"]:
                    Transform_Clients( Rework, ups )
    return
