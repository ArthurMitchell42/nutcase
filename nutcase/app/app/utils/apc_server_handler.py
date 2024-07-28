from flask import current_app

import socket
from struct import pack, unpack_from
import re
import time

from app.utils import format_to_text
from app.utils import apc_to_nut
from app.utils import rework_data

# ===================================================================================================
# Strip_Units - A list of variables that will be processed if the apc_strip_units option is active
# ===================================================================================================
Strip_List = [
    "LINEV",
    "LOADPCT",
    "BCHARGE",
    "TIMELEFT",
    "MBATTCHG",
    "MINTIMEL",
    "MAXTIME",
    "LOTRANS",
    "HITRANS",
    "BATTV",
    "TONBATT",
    "CUMONBATT",
    "NOMINV",
    "NOMBATTV",
    "MAXLINEV",
    "MINLINEV",
    "LINEFREQ",
    "OUTPUTV",
    "DWAKE",
    "DSHUTD",
    "RETPCT",
    "ITEMP",
    "DLOWBATT",
    "HUMIDITY",
    "AMBTEMP"
]

def Strip_Units(Scrape_Data):
    for v in Scrape_Data['ups_list'][0]['variables']:
        if v['name'] in Strip_List:
            From = format_to_text.Get_NUT_Variable(Scrape_Data['ups_list'][0], v['name'])
            To = str(apc_to_nut.Strip_Numeric(From))
            current_app.logger.debugvv("Striping {} From {} To {}".format(v['name'], From, To))
            format_to_text.Set_NUT_Variable(Scrape_Data['ups_list'][0], v['name'], To)
    return

# ===================================================================================================
# Query_APC_NIS_Socket
# ===================================================================================================
def Query_APC_NIS_Socket(Target_Address, Target_Port, Command):
    Skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Skt.settimeout(10)
    Packet = pack('>H6s', len(Command), Command)

    try:
        Skt.connect((Target_Address, Target_Port))
        Skt.send(Packet)
        time.sleep(5.0)
        Data = Skt.recv(4096 * 2)
        if len(Data) == 2:
            current_app.logger.debug('Short data so retying')
            time.sleep(1.0)
            Data2 = Skt.recv(4096 * 2)
            c = "2s{}s".format(len(Data2))
            Data = pack(c, Data, Data2)

        Skt.close()
    except Exception as Error:
        current_app.logger.error('Unable to connect to APC server: {}'.format(Error))
        return False, []

    return True, Data

# ===================================================================================================
# Parse_Packet_To_Lines
# ===================================================================================================
def Parse_Packet_To_Lines(Byte_Data):
    if len(Byte_Data) < 3:
        current_app.logger.debug('Short response from server: {} bytes'.format(len(Byte_Data)))
        return []

    Lines = []
    Offset = 0
    while True:
        Line_Length_tup = unpack_from('>H', Byte_Data, Offset)
        Offset += 2
        Line_Length = Line_Length_tup[0]
        if Line_Length == 0:
            break

        struct_format = '{}b'.format(Line_Length)
        Byte_tup = unpack_from(struct_format, Byte_Data, Offset)
        Offset += Line_Length

        Line = ''
        for item in Byte_tup:
            Line += chr(item)

        Lines.append(Line)
    return Lines

# ===================================================================================================
# Find_Vaiable_By_Name
# ===================================================================================================
def Find_Variable_By_Name(Name, Variables):
    return next((sub for sub in Variables if sub['name'] == Name), None)

# ===================================================================================================
# Format_APC_Data
# ===================================================================================================
def Format_APC_Data(Scrape_Lines):
    Line_Pattern = re.compile(r"^([A-Za-z0-9 ]+)\s*:\s+(.*)$")

    Variables = []
    for Line in Scrape_Lines:
        matches = re.search(Line_Pattern, Line)
        if matches:
            Variables.append({
                "name":  matches.group(1).strip(),
                "value": matches.group(2).strip()
            })
        else:
            current_app.logger.warning("No line match for {}".format(Line))

    if Version := Find_Variable_By_Name("VERSION", Variables):
        Server_Version = Version["value"]
    elif Version := Find_Variable_By_Name("RELEASE", Variables):
        Server_Version = Version["value"]
    else:
        Server_Version = "Not found"

    if Name := Find_Variable_By_Name("UPSNAME", Variables):
        UPS_Name = Name["value"]
    else:
        UPS_Name = "Not found"

    UPS_Description = "N/A"
    if Name := Find_Variable_By_Name("MODEL", Variables):
        UPS_Description = Name["value"]
    elif Name := Find_Variable_By_Name("APCMODEL", Variables):
        UPS_Description = Name["value"]
    else:
        UPS_Description = "---"

    if Name := Find_Variable_By_Name("HOSTNAME", Variables):
        UPS_Description += " @ " + Name["value"]
    elif Name := Find_Variable_By_Name("UPSMODE", Variables):
        UPS_Description += " @ " + Name["value"]
    else:
        UPS_Description += " @ ---"

    UPS = {}
    UPS["name"] = UPS_Name
    UPS["description"] = UPS_Description
    UPS["variables"] = Variables

    Scrape_Data = {}
    Scrape_Data["nutcase_version"] = current_app.config['APP_NAME'] + \
                                        " " + current_app.config['APP_VERSION']
    Scrape_Data["server_version"]  = Server_Version
    Scrape_Data["mode"]            = "apc"
    Scrape_Data["ups_list"]        = [UPS]
    Scrape_Data["debug"]           = Scrape_Lines

    return True, Scrape_Data

# ===================================================================================================
# Scrape entry point: Scrape_APC_Server
# ===================================================================================================
def Get_APC_Log(Target_Address, Target_Port = 3551):
    current_app.logger.debug("Getting logs from APC server, address {} port {}".format(
                                    Target_Address, Target_Port))

    Command = b'events'
    Status, Byte_Data = Query_APC_NIS_Socket(Target_Address, Target_Port, Command)
    if Status:
        current_app.logger.debug("APC Log retrival successful.")
    else:
        current_app.logger.warning("APC Log retrival unsuccessful.")
        return False, {}

    Scrape_Lines = Parse_Packet_To_Lines(Byte_Data)

    return Scrape_Lines

# ===================================================================================================
# Scrape entry point: Scrape_APC_Server
# ===================================================================================================
def Scrape_APC_Server(Target_Address, Target_Port = 3551):
    current_app.logger.debug("Scrape started of APC server, address {} port {}".format(
                                        Target_Address, Target_Port))

    # ===================================================================================
    # 1. Scrape the byte data from the server
    # 2. Split the NIS format byte stream to a list of lines as strings
    # 3. Parse the lines returned to make the Scrape_Data dictionary
    # ===================================================================================
    # Byte_Data = Load_Data()
    # Status = True
    Command = b'status'
    Status, Byte_Data = Query_APC_NIS_Socket(Target_Address, Target_Port, Command)
    if Status:
        current_app.logger.debug("Scrape APC log successful.")
    else:
        current_app.logger.warning("Scrape APC log unsuccessful.")
        return False, {}

    # Scrape_Lines = Test_Data_Back_UPS_ES_700G
    # Scrape_Lines = Test_Data_Back_UPS_RS_1500
    # Scrape_Lines = Test_Data_Smart_UPS_600
    # Scrape_Lines = Test_Data_Back_UPS_BF500
    Scrape_Lines = Parse_Packet_To_Lines(Byte_Data)

    Status, Scrape_Data = Format_APC_Data(Scrape_Lines)
    if Status:
        current_app.logger.debugv("Scrape_Data constructed.")
        Scrape_Data["server_address"] = Target_Address
        Scrape_Data["server_port"]    = Target_Port
        Scrape_Data['ups_list'][0]["server_address"] = Target_Address
        Scrape_Data['ups_list'][0]["server_port"]    = Target_Port

        UPSNAME = format_to_text.Get_NUT_Variable(Scrape_Data['ups_list'][0], 'UPSNAME')
        if UPSNAME:
            if " " in UPSNAME:
                UPSNAME = UPSNAME.replace(" ", "_")
                format_to_text.Set_NUT_Variable(Scrape_Data['ups_list'][0], 'UPSNAME', UPSNAME)

        if current_app.config['APC_STRIP_UNITS'] is True:
            Strip_Units(Scrape_Data)

        apc_to_nut.Translate_APC_To_NUT(Scrape_Data)

        rework_data.Rework_Variables(Scrape_Data)
    else:
        current_app.logger.warning("Scrape APC unsuccessful.")

    current_app.logger.debug("Scrape_Data: {}".format(Scrape_Data))
    return Status, Scrape_Data
