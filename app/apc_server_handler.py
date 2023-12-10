import logging
import logging.handlers

import socket
from struct import pack, unpack, unpack_from
import re
import time
import pickle

import globals

#=======================================================================
# Connect to the app log
#=======================================================================
log = logging.getLogger('__main__.' + __name__)

Test_Data_Back_UPS_RS_1500 = [
    "APC      : 001,037,0906",
    "DATE     : Sun Apr 26 17:22:22 EDT 2009",
    "HOSTNAME : mail.kroptech.com",
    "VERSION  : 3.14.2 (10 September 2007) redhat",
    "UPSNAME  : ups0",
    "CABLE    : USB Cable",
    "MODEL    : Back-UPS RS 1500",
    "UPSMODE  : Stand Alone",
    "STARTTIME: Sun Apr 26 10:22:46 EDT 2009",
    "STATUS   : ONLINE",
    "LINEV    : 123.0 Volts",
    "LOADPCT  :  24.0 Percent Load Capacity",
    "BCHARGE  : 100.0 Percent",
    "TIMELEFT : 144.5 Minutes",
    "MBATTCHG : 5 Percent",
    "MINTIMEL : 3 Minutes",
    "MAXTIME  : 0 Seconds",
    "SENSE    : Medium",
    "LOTRANS  : 097.0 Volts",
    "HITRANS  : 138.0 Volts",
    "ALARMDEL : Always",
    "BATTV    : 26.8 Volts",
    "LASTXFER : Low line voltage",
    "NUMXFERS : 0",
    "TONBATT  : 0 seconds",
    "CUMONBATT: 0 seconds",
    "XOFFBATT : N/A",
    "SELFTEST : NO",
    "STATFLAG : 0x07000008 Status Flag",
    "MANDATE  : 2003-05-08",
    "SERIALNO : JB0319033692",
    "BATTDATE : 2001-09-25",
    "NOMINV   : 120",
    "NOMBATTV :  24.0",
    "FIRMWARE : 8.g6 .D USB FW:g6",
    "APCMODEL : Back-UPS RS 1500",
    "END APC  : Sun Apr 26 17:22:32 EDT 2009"
    ]

Test_Data_Smart_UPS_600 = [
    "APC      : 001,048,1088",
    "DATE     : Fri Dec 03 16:49:24 EST 1999",
    "HOSTNAME : daughter",
    "RELEASE  : 3.7.2",
    "CABLE    : APC Cable 940-0024C",
    "MODEL    : APC Smart-UPS 600",
    "UPSMODE  : Stand Alone",
    "UPSNAME  : SU600",
    "LINEV    : 122.1 Volts",
    "MAXLINEV : 123.3 Volts",
    "MINLINEV : 122.1 Volts",
    "LINEFREQ : 60.0 Hz",
    "OUTPUTV  : 122.1 Volts",
    "LOADPCT  :  32.7 Percent Load Capacity",
    "BATTV    : 26.6 Volts",
    "BCHARGE  : 095.0 Percent",
    "MBATTCHG : 15 Percent",
    "TIMELEFT :  19.0 Minutes",
    "MINTIMEL : 3 Minutes",
    "SENSE    : Medium",
    "DWAKE    : 000 Seconds",
    "DSHUTD   : 020 Seconds",
    "LOTRANS  : 106.0 Volts",
    "HITRANS  : 129.0 Volts",
    "RETPCT   : 010.0 Percent",
    "STATFLAG : 0x08 Status Flag",
    "STATUS   : ONLINE",
    "ITEMP    : 34.6 C Internal",
    "ALARMDEL : Low Battery",
    "LASTXFER : Unacceptable Utility Voltage Change",
    "SELFTEST : NO",
    "STESTI   : 336",
    "DLOWBATT : 05 Minutes",
    "DIPSW    : 0x00 Dip Switch",
    "REG1     : N/A",
    "REG2     : N/A",
    "REG3     : 0x00 Register 3",
    "MANDATE  : 03/30/95",
    "SERIALNO : 13035861",
    "BATTDATE : 05/05/98",
    "NOMOUTV  : 115.0",
    "NOMBATTV :  24.0",
    "HUMIDITY : N/A",
    "AMBTEMP  : N/A",
    "EXTBATTS : N/A",
    "BADBATTS : N/A",
    "FIRMWARE : N/A",
    "APCMODEL : 6TD",
    "END APC  : Fri Dec 03 16:49:25 EST 1999",
    ]

#====================================================================================================
# Debug load & save
#====================================================================================================
def Save_Data( Data ):
    Dict = { "raw": Data }
    with open('./scrap/raw_apc.pickle', 'wb') as handle:
        pickle.dump(Dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return

def Load_Data():
    with open('./scrap/raw_apc.pickle', 'rb') as handle:
        Dict = pickle.load(handle)
    return Dict["raw"]

#====================================================================================================
# Query_APC_NIS_Socket
#====================================================================================================
def Query_APC_NIS_Socket(Target_Address, Target_Port, Command):
    Skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Skt.settimeout(10)
    Packet = pack('>H6s', len(Command), Command)

    try:
        Skt.connect( (Target_Address, Target_Port) )
        Skt.send( Packet )
        time.sleep(5.0)
        Data = Skt.recv(4096)
        if len(Data) == 2:
            log.debug( 'Short data so retying' ) 
            time.sleep(1.0)
            Data2 = Skt.recv(4096)
            c = "2s{}s".format( len(Data2) )
            Data = pack(c, Data, Data2)

        Skt.close()
    except Exception as Error:
        log.error( 'Unable to connect to APC server: {}'.format(Error) ) 
        return False, []

    return True, Data

#====================================================================================================
# Parse_Packet_To_Lines
#====================================================================================================
def Parse_Packet_To_Lines( Byte_Data ):
    if len(Byte_Data) < 3:
        log.debug('Short response from server: {} bytes'.format( len(Byte_Data) ) )
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

        Lines.append( Line.rstrip('\n') )
    return Lines

#====================================================================================================
# Find_Vaiable_By_Name
#====================================================================================================
def Find_Variable_By_Name( Name, Variables ):
    return next((sub for sub in Variables if sub['name'] == Name), None)

#====================================================================================================
# Format_APC_Data
#====================================================================================================
def Format_APC_Data( Scrape_Lines ):
    Line_Pattern = re.compile("^([A-Za-z0-9 ]+)\s*:\s+(.*)$")

    Variables = []
    for Line in Scrape_Lines:
        matches = re.search(Line_Pattern, Line)
        if matches:
            Variables.append( {
                "name":  matches.group(1).strip(),
                "value": matches.group(2).strip()
            } )
        else:
            log.warning("No line match for {}".format(Line) ) 

    if Version := Find_Variable_By_Name( "VERSION", Variables ):
        Server_Version = Version["value"] 
    else:
        Server_Version = "Not found"

    if Name := Find_Variable_By_Name( "UPSNAME", Variables ):
        UPS_Name = Name["value"] 
    else:
        UPS_Name = "Not found"

    UPS_Description = "N/A"
    if Name := Find_Variable_By_Name( "MODEL", Variables ):
        UPS_Description = Name["value"] 
    elif Name := Find_Variable_By_Name( "APCMODEL", Variables ):
        UPS_Description = Name["value"] 
    else:
        UPS_Description = "---"
    
    if Name := Find_Variable_By_Name( "HOSTNAME", Variables ):
        UPS_Description += " @ " + Name["value"] 
    elif Name := Find_Variable_By_Name( "UPSMODE", Variables ):
        UPS_Description += " @ " + Name["value"] 
    else:
        UPS_Description += " @ ---"

    UPS = {}
    UPS["name"] = UPS_Name
    UPS["description"] = UPS_Description
    UPS["variables"] = Variables

    Scrape_Data = {}
    Scrape_Data["server_version"] = Server_Version
    Scrape_Data["ups_list"]       = [ UPS ]
    Scrape_Data["debug"]          = Scrape_Lines

    return True, Scrape_Data

#====================================================================================================
# Scrape entry point: Scrape_APC_Server
#====================================================================================================
def Get_APC_Log( Target_Address, Target_Port = 3551 ):
    log.debug( "Getting logs from APC server, address {} port {}".format( Target_Address, Target_Port ) ) 

    Command = b'events'
    Status, Byte_Data = Query_APC_NIS_Socket( Target_Address, Target_Port, Command )
    if Status:
        log.debug( "APC Log retrival successful." ) 
    else:
        log.warning( "APC Log retrival unsuccessful." )
        return False, {}

    Scrape_Lines = Parse_Packet_To_Lines( Byte_Data )
    log.debug( "Log lines:" ) 
    for Line in Scrape_Lines:
        log.debug( "  {}".format( Line) ) 

    return Scrape_Lines

#====================================================================================================
# Scrape entry point: Scrape_APC_Server
#====================================================================================================
def Scrape_APC_Server( Target_Address, Target_Port = 3551 ):
    log.debug( "Scrape started of APC server, address {} port {}".format( Target_Address, Target_Port ) ) 

    #====================================================================================
    # 1. Scrape the byte data from the server 
    # 2. Split the NIS format byte stream to a list of lines as strings
    # 3. Parse the lines returned to make the Scrape_Data dictionary
    #====================================================================================
    # Byte_Data = Load_Data()
    # Status = True
    Command = b'status'   # b'events'
    Status, Byte_Data = Query_APC_NIS_Socket( Target_Address, Target_Port, Command )
    if Status:
        log.debug( "Scrape successful." ) 
    else:
        log.warning( "Scrape unsuccessful." )
        return False, {}

    # Scrape_Lines = Test_Data_Back_UPS_RS_1500
    # Scrape_Lines = Test_Data_Smart_UPS_600
    Scrape_Lines = Parse_Packet_To_Lines( Byte_Data )

    Status, Scrape_Data = Format_APC_Data( Scrape_Lines )
    if Status:
        log.debug( "Scrape_Data constructed." ) 
        Scrape_Data["server_address"] = Target_Address
        Scrape_Data["server_port"]    = Target_Port
        if globals.Config:
            log.debug( "Reworking variables." ) 
        #     rework_data.Rework_Variables( Scrape_Data, globals.Config )
        else:
            log.debug( "Not reworking variables." ) 

        # Save_Data( Scrape_Data )
    else:
        log.warning( "Scrape unsuccessful." )

    return Status, Scrape_Data
