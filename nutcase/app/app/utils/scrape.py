from flask import current_app
from ipaddress import ip_address    # For parsing target addresses
from app.utils import webhook

from app.cache_controller.cache_controller import Scrape_Bucket
from app.utils.db_utils import Scan_DB_For_Device, Scan_DB_For_Server
from app.utils import rework_data

# ===================================================================================================
# Utility to parse and validate the target IP and port
# ===================================================================================================
def Validate_Target(Target_Param):
    Target_Address = ""
    Parameter_Target_Port = None

    Addr, Separator, Port = Target_Param.rpartition(':')

    if not Separator:
        Addr, Port = Port, None

    try:
        Target_Address = str(ip_address(Addr))
    except ValueError as Error:
        current_app.logger.error("Improper IP address for target {} Error {}".format(Addr, Error))
        return False, None, None

    if Port:
        if Port.isnumeric():
            Parameter_Target_Port = int(Port)
        else:
            current_app.logger.error("Improper port for target {}".format(Port))
            return False, Target_Address, None

    return True, Target_Address, Parameter_Target_Port

# ===================================================================================================
# Resolve the target server addrees and, optionally, port
# ===================================================================================================
def Resolve_Address_And_Port(params):
    Target_Resolved = False
    Target_Address  = None
    Parameter_Port = None

    if not params:
        return Target_Resolved, Target_Address, Parameter_Port

    if "target" in params:
        rtn, Target_Address, Parameter_Port = Validate_Target(params["target"])
        if rtn:
            Target_Resolved = True
    elif "addr" in params:
        try:
            Target_Address = str(ip_address(params["addr"]))
            Target_Resolved = True
        except ValueError as Error:
            current_app.logger.error("Improper IP address for addr {} Error {}".format(
                params["addr"], Error))

    if "port" in params:
        if params["port"].isnumeric():
            Parameter_Port = int(params["port"])
        else:
            current_app.logger.error("Improper port specified {}".format(params["port"]))
            Target_Resolved = False
    return Target_Resolved, Target_Address, Parameter_Port

# ===========================================================================================
# Check the mode (NUT or APC) from the URL parameters
# ===========================================================================================
def Check_Mode(URL_Parameters):
    Server_Type = "nut"        # Default protocol NUT
    Target_Port = 3493         # Default NUT port

    if URL_Parameters:
        if "mode" in URL_Parameters and URL_Parameters["mode"]:
            if URL_Parameters["mode"].lower() == "nut":
                Server_Type = "nut"
                Target_Port = 3493
            elif URL_Parameters["mode"].lower() == "apc":
                Server_Type = "apc"
                Target_Port = 3551   # Default APC port
            else:
                Server_Type = "none"
                current_app.logger.error("Unknown server mode requested: {}".format(
                    URL_Parameters["mode"]))

    return Server_Type, Target_Port

# ===========================================================================================
# Apply_Log_Data Apply log stauts to scrape data
# ===========================================================================================
def Apply_Log_Data(Scrape_Data, Target_Address):
    # =============================================================================================
    # Check the log status for server logs
    Svr_Log_Vals = Scan_DB_For_Server(Target_Address)
    Scrape_Data.update({"logs":
        {
        "total": [Svr_Log_Vals['info'], Svr_Log_Vals['warning'], Svr_Log_Vals['alert']],
        "unread": [Svr_Log_Vals['info_unread'], Svr_Log_Vals['warning_unread'],
                   Svr_Log_Vals['alert_unread']]
        }
        })

    if 'logs' in Scrape_Data:
        Log_Output = rework_data.Generate_Log_Entries(Svr_Log_Vals)
        Scrape_Data['logs'].update(Log_Output)

    # =============================================================================================
    # Check the log status for listed devices
    if 'ups_list' in Scrape_Data:
        for dev in Scrape_Data['ups_list']:
            Dev_Log_Vals = Scan_DB_For_Device(Target_Address, dev['name'])
            dev.update({"logs":
                {
                "total": [Dev_Log_Vals['info'], Dev_Log_Vals['warning'], Dev_Log_Vals['alert']],
                "unread": [Dev_Log_Vals['info_unread'], Dev_Log_Vals['warning_unread'],
                            Dev_Log_Vals['alert_unread']]
                }
                })

            if 'logs' in Scrape_Data:
                Log_Output = rework_data.Generate_Log_Entries(Dev_Log_Vals)
                dev['logs'].update(Log_Output)
    return

# ===================================================================================
# Get_Scrape_Data
# ===================================================================================
def Get_Scrape_Data(URL_Parameters):
    Server_Type, Target_Port = Check_Mode(URL_Parameters)
    Target_Resolved, Target_Address, Parameter_Port = Resolve_Address_And_Port(URL_Parameters)

    if Parameter_Port:
        Target_Port = int(Parameter_Port)

    if not Target_Resolved:
        return False, {}

    # ===================================================================================
    # Request a scrape
    # ===================================================================================
    Bucket = Scrape_Bucket(Target_Address, Target_Port, Server_Type)
    current_app.config['CACHE_QUEUE'].put(Bucket)

    ready_flag = Bucket.get_flag()
    ready_flag.acquire()
    Ready = ready_flag.wait(timeout=current_app.config['SCRAPE_TIMEOUT'])

    # Check time out
    if not Ready:
        current_app.logger.warning("GSD request timed out")

    ready_flag.release()

    Scrape_Return = Bucket.result
    Scrape_Data = Bucket.scrape_data

    current_app.logger.debugv("Get_Scrape_Data: Scrape_Data {} Scrape_Return {}".format(
                                                                    Scrape_Data, Scrape_Return))

    if not Scrape_Return:
        webhook.Call_Webhook(current_app, "fail",
                            {"status": "down", "msg": "ScrapeFail-{}".format(Target_Address)})
    else:
        # =========================================================================================
        # Check the log status for server and device
        Apply_Log_Data(Scrape_Data, Target_Address)

        webhook.Call_Webhook(current_app, "ok",
                            {"status": "up", "msg": "ScrapeOK-{}".format(
                                Target_Address)})

    return Scrape_Return, Scrape_Data
