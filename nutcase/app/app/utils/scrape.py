from flask import current_app

from ipaddress import ip_address    # For parsing target addresses

from app.utils import nut_server_handler
from app.utils import apc_server_handler
from app.utils import cache_control
from app.utils import webhook

#====================================================================================================
# Utility to parse and validate the target IP and port
#====================================================================================================
def Validate_Target( Target_Param ):
    Target_Address = "" 
    Parameter_Target_Port = None

    Addr, Separator, Port = Target_Param.rpartition(':')

    if not Separator:
        Addr, Port = Port, None

    try:
        Target_Address = str(ip_address(Addr))
    except ValueError as Error:
        current_app.logger.error("Improper IP address for target {}".format(Addr))
        return False, None, None

    if Port: 
        if Port.isnumeric():
            Parameter_Target_Port = int(Port)
        else:
            current_app.logger.error("Improper port for target {}".format(Port))
            return False, Target_Address, None

    return True, Target_Address, Parameter_Target_Port

#====================================================================================================
# Resolve the target server addrees and, optionally, port
#====================================================================================================
def Resolve_Address_And_Port( params ):
    Target_Resolved = False
    Target_Address  = None
    Parameter_Port = None

    if "target" in params:
        rtn, Target_Address, Parameter_Port = Validate_Target(params["target"])
        if rtn:
            Target_Resolved = True
    elif "addr" in params:
        try:
            Target_Address = str(ip_address(params["addr"]))
            Target_Resolved = True
        except ValueError as Error:
            current_app.logger.error("Improper IP address for addr {}".format(params["addr"]))

    if "port" in params:
        if params["port"].isnumeric():
            Parameter_Port = params["port"]
        else:
            current_app.logger.error("Improper port specified {}".format( params["port"] ))
            Target_Resolved = False
    return Target_Resolved, Target_Address, Parameter_Port

#============================================================================================
# Check the mode (NUT or APC) from the URL parameters
#============================================================================================
def Check_Mode( URL_Parameters ):
    Server_Type = "nut" # Server_Protocol.NUT
    Target_Port = 3493         # Default NUT port, may be overridden below by parameters
    
    if "mode" in URL_Parameters:
        if URL_Parameters["mode"].lower() == "nut":
            Server_Type = "nut" # Server_Protocol.NUT
            Target_Port = 3493
        elif URL_Parameters["mode"].lower() == "apc":
            Server_Type = "apc" # Server_Protocol.APC
            Target_Port = 3551 # Default APC port, may be overridden below by parameters
        else:
            Server_Type = "none" # Server_Protocol.NONE
            current_app.logger.error("Unknown server mode requested: {}".format( URL_Parameters["mode"][0] ))

    return Server_Type, Target_Port

#====================================================================================
# Get_Scrape_Data
#====================================================================================
def Get_Scrape_Data( URL_Parameters ):

    Server_Type, Target_Port = Check_Mode( URL_Parameters )
    if not Server_Type:
        return False, {}

    Target_Resolved, Target_Address, Parameter_Port = Resolve_Address_And_Port( URL_Parameters )

    if Parameter_Port:
        Target_Port = int(Parameter_Port)


    if not Target_Resolved:
        return False, {}

    #====================================================================================
    # Check the cache to see if we need to re-scrape
    #====================================================================================
    Scrape_Return, Scrape_Data = cache_control.Fetch_From_Cache( Target_Address, Target_Port )

    if not Scrape_Data:
        #====================================================================================
        # Get the server data based on type (NUT/APC) as it can't be sourced from the cache
        #====================================================================================
        if Server_Type == "nut": # Server_Protocol.NUT:
            Scrape_Return, Scrape_Data = nut_server_handler.Scrape_NUT_Server( Target_Address, Target_Port )
        elif Server_Type == "apc": # Server_Protocol.APC:
            Scrape_Return, Scrape_Data = apc_server_handler.Scrape_APC_Server( Target_Address, Target_Port )
        cache_control.Add_To_Cache( Target_Address, Target_Port, Scrape_Data )

    cache_control.Tidy_Cache()

    current_app.logger.debug("Get_Scrape_Data: Scrape_Data {}".format( Scrape_Data ))

    if not Scrape_Return:
        webhook.Call_Webhook( current_app, "fail", { "status": "down", "msg": "ScrapeFail-{}".format(Target_Address) } )
    else:
        webhook.Call_Webhook( current_app, "ok", { "status": "up", "msg": "ScrapeOK-{}".format(Target_Address) } )

    return Scrape_Return, Scrape_Data
