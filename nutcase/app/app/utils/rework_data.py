from flask import current_app

import time         # To format time variables
import re           # for splitting status strings

from app.utils import format_to_text
from app.utils import configuration

# ===================================================================================================
# Transform a variable to an enumerated string
# ===================================================================================================
def Transform_Simple_Enum(Var, Rework):
    New_Var = {"name": Rework["to"], "value": ""}

    Search_String = Var["value"]
    current_app.logger.debugv("SimpEnum: Looking for {} in {}".format(Search_String,
                                                                      Rework["control"]["from"]))

    if Search_String in Rework["control"]["from"]:
        Index = Rework["control"]["from"].index(Search_String)
        New_Value = Rework["control"]["to"][Index]
    else:
        New_Value = Rework["control"]["default"]

    New_Var["value"] = New_Value
    return New_Var

# ===================================================================================================
# Transform a variable to an enumerated string
# ===================================================================================================
def Transform_Composite_Enum(Var, Rework):
    New_Var = {"name": Rework["to"], "value": ""}
    Found_Match = False

    if 'join' in Rework["control"]:
        Join = Rework["control"]["join"]
    else:
        Join = " "

    Search_List = re.split(r' |:|;|-|\.|/|\\', Var["value"])
    current_app.logger.debug("CompEnum: Looking for {} in {}".format(Search_List,
                                                                      Rework["control"]["from"]))

    Comp_Value = ""
    for Search_String in Search_List:
        if Search_String in Rework["control"]["from"]:
            Index = Rework["control"]["from"].index(Search_String)
            if len(Comp_Value) == 0:
                Comp_Value = Rework["control"]["to"][Index]
            else:
                Comp_Value += Join + Rework["control"]["to"][Index]
            Found_Match = True

    if not Found_Match:
        Comp_Value = Rework["control"]["default"]

    New_Var["value"] = Comp_Value
    return New_Var

# ==================================================================================================
# Transform a variable to a ratio
# ==================================================================================================
def Transform_Ratio(Var, Rework, UPS):
    New_Var = {"name": Rework["to"], "value": ""}

    if Nominal_Power := format_to_text.Get_NUT_Variable(UPS, Rework["control"]):
        Nominal_Power = int(float(Nominal_Power))
    else:
        Nominal_Power = 0

    if Device := configuration.Get_Device(UPS['server_address'], UPS['name']):
        if 'power' in Device:
            try:
                Nominal_Power = float(Device['power'])
                current_app.logger.debug("Using power value from config {}".format(Nominal_Power))
            except Exception:
                Nominal_Power = 0.0
                current_app.logger.error(
                    "Can't use power value from server config {}".format(Device['power']))

    Percent_Power = float(Var["value"])

    Ratio = Nominal_Power * (Percent_Power / 100)
    New_Var["value"] = str(round(Ratio, 1))
    return New_Var

# ==================================================================================================
# Transform a variable to a time string
# ==================================================================================================
def Transform_Time(Var, Rework):
    New_Var = {"name": Rework["to"], "value": ""}
    formatted_time = time.strftime(Rework["control"], time.gmtime(int(Var["value"])))
    New_Var["value"] = formatted_time
    return New_Var

# ==================================================================================================
# Parse data and add transformed variables
# ==================================================================================================
def Transform_Variable(Var, Rework, UPS):
    current_app.logger.debug("Transforming: {} with transform {} and appending to UPS {}".format(
        Var["name"], Rework["style"], UPS["name"]))

    if Rework["style"].lower() == "time":
        New_Var = Transform_Time(Var, Rework)
        if New_Var:
            UPS["variables"].append(New_Var)
    elif Rework["style"].lower() == "ratio":
        New_Var = Transform_Ratio(Var, Rework, UPS)
        if New_Var:
            UPS["variables"].append(New_Var)
    elif Rework["style"].lower() == "simple-enum":
        New_Var = Transform_Simple_Enum(Var, Rework)
        if New_Var:
            UPS["variables"].append(New_Var)
    elif Rework["style"].lower() == "comp-enum":
        New_Var = Transform_Composite_Enum(Var, Rework)
        if New_Var:
            UPS["variables"].append(New_Var)
    else:
        current_app.logger.debug("Unknown transform string {}".format(Rework["style"]))
    return

# ===================================================================================================
# Transform_Client_Count
# ===================================================================================================
def Transform_Client_Count(UPS, Rework):
    current_app.logger.debug("Applying transform {} and appending to UPS {}".format(
        Rework["style"], UPS["name"]))

    New_Var = {"name": Rework["to"], "value": ""}

    Expected = 0
    Parse_Error = False
    Exp_Entry = Rework["control"][0]
    if isinstance(Exp_Entry, str):
        if Exp_Entry.lower() == 'auto':
            Device_Clients = None
            Device = configuration.Get_Device(UPS['server_address'], UPS['name'])
            if 'clients' in Device:
                Device_Clients = Device['clients']

            Expected = len(Device_Clients)
        else:
            try:
                Expected = int(Exp_Entry)
            except Exception as Error:
                current_app.logger.error(f"Could not use rework control {Rework}, {Error}")
                current_app.config.update(CONFIG_ERROR=True)
                Parse_Error = True
    elif isinstance(Exp_Entry, int):
        Expected = int(Exp_Entry)
    else:
        current_app.logger.error(f"Could not use count in rework control {Rework}")
        current_app.config.update(CONFIG_ERROR=True)
        Parse_Error = True

    diff = len(UPS["clients"]) - Expected

    if diff == 0:
        Display = Rework["control"][2].format(d=diff, c=Expected)
    elif diff > 0:
        Display = Rework["control"][3].format(d=abs(diff), c=Expected)
    elif diff < 0:
        Display = Rework["control"][1].format(d=abs(diff), c=Expected)

    if Parse_Error:
        New_Var["value"] = "Error"
    else:
        New_Var["value"] = Display
    return New_Var

# ===================================================================================================
# Transform_Client_Check
# ===================================================================================================
def Transform_Client_Check(UPS, Rework):
    current_app.logger.debug("Applying transform {} and appending to UPS {}".format(
        Rework["style"], UPS["name"]))

    New_Var = {"name": Rework["to"], "value": ""}

    Missing = []

    Expected_Clients = []
    Parse_Error = False
    Client_Control = Rework["control"]
    if isinstance(Client_Control, str):
        if Client_Control.lower() == 'auto':
            Device = configuration.Get_Device(UPS['server_address'], UPS['name'])
            if 'clients' in Device:
                Expected_Clients = Device['clients']
        else:
            current_app.logger.error(f"Could not use clients in rework control {Rework}")
            current_app.config.update(CONFIG_ERROR=True)
            Parse_Error = True
    elif isinstance(Client_Control, list):
        Expected_Clients = Client_Control
    else:
        current_app.logger.error(f"Could not use clients in rework control {Rework}")
        current_app.config.update(CONFIG_ERROR=True)
        Parse_Error = True

    for a in Expected_Clients:
        if a not in UPS['clients']:
            Missing.append(a)

    if len(Missing) > 0:
        Missing_String = ""
        for m in Missing:
            Missing_String += m + " "
        Display = "Missing {} {}".format(len(Missing), Missing_String)
    else:
        Display = "All present"

    if Parse_Error:
        New_Var["value"] = "Error"
    else:
        New_Var["value"] = Display
    return New_Var

# ===================================================================================================
# Transform_Clients
# ===================================================================================================
def Transform_Clients(Rework, UPS):
    current_app.logger.debug("Transforming: clients of {} with transform {}".format(
                                                        UPS["name"], Rework["style"]))

    if Rework["style"].lower() == "cl-count":
        New_Var = Transform_Client_Count(UPS, Rework)
        if New_Var:
            UPS["variables"].append(New_Var)
    elif Rework["style"].lower() == "cl-check":
        New_Var = Transform_Client_Check(UPS, Rework)
        if New_Var:
            UPS["variables"].append(New_Var)
    return

# ===================================================================================================
# Generate_Log_Entries
# ===================================================================================================
def Generate_Log_Entries(Vals):
    # current_app.logger.debug("Generate_Log_Entries: Log_Entries {}".format(Log_Entries))
    Entries = {}
    for lf in current_app.config["REWORK"]:
        if "style" in lf:
            if lf["style"] == "nutcase_logs":
                Var = lf['control'].format(
                    info_total=Vals['info'],
                    warning_total=Vals['warning'],
                    alert_total=Vals['alert'],

                    info_unread=Vals['info_unread'],
                    warning_unread=Vals['warning_unread'],
                    alert_unread=Vals['alert_unread'],

                    info_read=Vals['info'] - Vals['info_unread'],
                    warning_read=Vals['warning'] - Vals['warning_unread'],
                    alert_read=Vals['alert'] - Vals['alert_unread'],
                    )
                Entries[lf["to"]] = Var

    return Entries

# ===================================================================================================
# region Main
# Parse data and add transformed variables
# ===================================================================================================
def Rework_Variables(Scrape_Data):
    Status = False

    if not Scrape_Data or ("ups_list" not in Scrape_Data):
        return Status
    if not Scrape_Data["ups_list"]:
        return Status

    for ups in Scrape_Data["ups_list"]:                # Loop through the UPS devices
        if not ups["variables"]:
            continue
        for var in ups["variables"]:                   # Loop through each variable for this UPS
            # Is the variable in the list of ones to transform?
            if var["name"] in current_app.config["REWORK_VAR_LIST"]:
                # Loop through the transforms in the control file
                for Rework in current_app.config["REWORK"]:
                    if "from" in Rework:
                        if Rework["from"] == var["name"]:
                            Transform_Variable(var, Rework, ups)
                            Status = True

        if ups["name"] in current_app.config["REWORK_VAR_LIST"]:
            # Loop through the transforms in the control file
            for Rework in current_app.config["REWORK"]:
                if "from" in Rework:
                    if Rework["from"] == ups["name"]:
                        Transform_Clients(Rework, ups)
                        Status = True
    return Status
