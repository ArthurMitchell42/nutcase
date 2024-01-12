import logging
import time         # To format time variables 
import re           # for splitting status strings

#=======================================================================
# Connect to the app log
#=======================================================================
log = logging.getLogger('__main__.' + __name__)

#====================================================================================================
# Helper routine to get the value from a names variable
#====================================================================================================
def Get_NUT_Variable( ups, Variable_Name ):
    Variable = next((sub for sub in ups["variables"] if sub['name'] == Variable_Name), None)
    if Variable:
        Value = str( Variable["value"] )
    else:
        Value = None
    return Value

#====================================================================================================
# Transform a variable to an enumerated string
#====================================================================================================
def Transform_Simple_Enum( Var, Rework ):
    New_Var = {"name": Rework["to"], "value": ""}

    Search_String = Var["value"]
    log.debug("SimpEnum: Looking for {} in {}".format( Search_String, Rework["control"]["from"] )) 

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
    log.debug("CompEnum: Looking for {} in {}".format( Search_List, Rework["control"]["from"] )) 

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

    if Nominal_Power := Get_NUT_Variable( UPS, Rework["control"] ):
        Nominal_Power = int( float(Nominal_Power) )
    else:
        Nominal_Power = 0
    Percent_Power = int( Var["value"] )

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
    log.debug("Transforming: {} with transform {} and appending to UPS {}".format( Var["name"], Rework["style"], UPS["name"] ))    

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
        log.debug("Unknown transform string {}".format( Rework["style"] ))    

    return

#====================================================================================================
# Parse data and add transformed variables
#====================================================================================================
def Rework_Variables( Scrape_Data, Config ):
    for ups in Scrape_Data["ups_list"]:                     # Loop through the UPS devices
        for var in ups["variables"]:                        # Loop through each variable for this UPS
            if var["name"] in Config["rework_var_list"]:    # Is the variable in the list of ones to transform?
                for Rework in Config["rework"]:             # Loop through the transforms in the control file
                    if Rework["from"] == var["name"]:
                        Transform_Variable( var, Rework, ups )

    return
