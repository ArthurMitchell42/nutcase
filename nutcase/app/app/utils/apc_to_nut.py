from flask import current_app

import re

from app.utils import format_to_text

Constants_STATFLAG = [
# /* bit values for APC UPS Status Byte (ups->Status) */ 
    { "Define": "UPS_calibration" , "Mask":  0x00000001, "Status": "CAL",   },
    { "Define": "UPS_trim"        , "Mask":  0x00000002, "Status": "TRIM",  },
    { "Define": "UPS_boost"       , "Mask":  0x00000004, "Status": "BOOST", },
    { "Define": "UPS_online"      , "Mask":  0x00000008, "Status": "OL",    },
    { "Define": "UPS_onbatt"      , "Mask":  0x00000010, "Status": "OB",    },
    { "Define": "UPS_overload"    , "Mask":  0x00000020, "Status": "OVER",  },
    { "Define": "UPS_battlow"     , "Mask":  0x00000040, "Status": "LB",    },
    { "Define": "UPS_replacebatt" , "Mask":  0x00000080, "Status": "RB",    },
# /*Extended bit values added by apcupsd */ 
    { "Define": "UPS_commlost"    , "Mask":  0x00000100, "Status": "",      },   #   /* Communications with UPS lost */ 
    { "Define": "UPS_shutdown"    , "Mask":  0x00000200, "Status": "SD",    },   #   /* Shutdown in progress */ 
    { "Define": "UPS_slave"       , "Mask":  0x00000400, "Status": "",      },   #   /* Set if this is a slave */ 
    { "Define": "UPS_slavedown"   , "Mask":  0x00000800, "Status": "",      },   #   /* Slave not responding */ 
    { "Define": "UPS_onbatt_msg"  , "Mask":  0x00020000, "Status": "",      },   #   /* Set when UPS_ONBATT message is sent*/ 
    { "Define": "UPS_fastpoll"    , "Mask":  0x00040000, "Status": "",      },   #   /* Set on power failure to poll faster */  
    { "Define": "UPS_shut_load"   , "Mask":  0x00080000, "Status": "",      },   #   /* Set when BatLoad <= percent */  
    { "Define": "UPS_shut_btime"  , "Mask":  0x00100000, "Status": "",      },   #   /* Set when time on batts > maxtime */ 
    { "Define": "UPS_shut_ltime"  , "Mask":  0x00200000, "Status": "SD",    },   #   /* Set when TimeLeft <= runtime */ 
    { "Define": "UPS_shut_emerg"  , "Mask":  0x00400000, "Status": "FSD",   },   #   /* Set when battery power has failed */ 
    { "Define": "UPS_shut_remote" , "Mask":  0x00800000, "Status": "",      },   #   /* Set when remote shutdown */ 
    { "Define": "UPS_plugged"     , "Mask":  0x01000000, "Status": "",      },   #   /* Set if computer is plugged into UPS */ 
    { "Define": "UPS_battpresent" , "Mask":  0x04000000, "Status": "",      },   #   /* Indicates if battery is connected */ 
]

#===========================================================
# Strip_Numeric
#===========================================================
def Strip_Numeric( Text ):
    Value = None
    Num_Text_Pattern = re.compile(r"^( )*([0-9\.]+)( )*(.*)$")

    Num_Text_Match = re.search( Num_Text_Pattern, Text )
    if Num_Text_Match:
        Value_Text = Num_Text_Match.group(2)
        if '.' in Value_Text:
            Value = float( Value_Text )
        else:
            Value = int( Value_Text )
    return Value

#===========================================================
# Strip_Hex
#===========================================================
def Strip_Hex( Text ):
    Value = None
    Hex_Text_Pattern = re.compile(r"^( )*([0-9A-FX]+)?( )*(.*)$")

    Hex_Text_Match = re.search( Hex_Text_Pattern, Text.upper() )
    if Hex_Text_Match:
        Value_Text = Hex_Text_Match.group(2)
        Value = int(Value_Text, 16)
    return Value

#===========================================================
# Other_Parameters
#===========================================================
def Other_Parameters( Scrape_Data ):
    Model = 'Unknown'

    MODEL = format_to_text.Get_NUT_Variable( Scrape_Data['ups_list'][0], 'MODEL' )
    if MODEL:
        Model = MODEL
    Scrape_Data['ups_list'][0]['variables'].append( {'name': 'ups.model', 'value': Model} )
    return

#===========================================================
# Time_Controls
#===========================================================
def Time_Controls( Scrape_Data ):
# DWAKE
# The amount of time the UPS will wait before restoring power to your equipment after a power off
# condition when the power is restored.
# DSHUTD
# The grace delay that the UP
    DWake = '0'
    DShutD = '0'

    DWAKE = format_to_text.Get_NUT_Variable( Scrape_Data['ups_list'][0], 'DWAKE' )
    if DWAKE:
        DWake = str(Strip_Numeric( DWAKE ))
    Scrape_Data['ups_list'][0]['variables'].append( {'name': 'ups.delay.shutdown', 'value': DWake} )

    DSHUTD = format_to_text.Get_NUT_Variable( Scrape_Data['ups_list'][0], 'DSHUTD' )
    if DSHUTD:
        DShutD = str(Strip_Numeric( DSHUTD ))
    Scrape_Data['ups_list'][0]['variables'].append( {'name': 'ups.delay.start', 'value': DShutD} )

    return

#===========================================================
# Beeper_Status
#===========================================================
def Beeper_Status( Scrape_Data ):
# BEEPSTATE [ 0 | T | L | N ]
#     Alarm delay.
#     0 : Zero delay after power fails.
#     T : When power fails plus 30 seconds.
#     L : When low battery occurs.
#     N : Never.
    BeepState = 'Unknown'
    BeepStateText = 'Unknown'

    BEEPSTATE = format_to_text.Get_NUT_Variable( Scrape_Data['ups_list'][0], 'BEEPSTATE' )
    if BEEPSTATE:
        if BEEPSTATE == '0' or BEEPSTATE == 'T' or BEEPSTATE == 'L':
            BeepState = 'enabled'
        elif BEEPSTATE == 'N':
            BeepState = 'disabled'
    else:
        ALARMDEL = format_to_text.Get_NUT_Variable( Scrape_Data['ups_list'][0], 'ALARMDEL' )
        if ALARMDEL:
            BeepStateText = ALARMDEL
            if ALARMDEL.lower() == 'no alarm':
                BeepState = 'disabled'
            else:
                BeepState = 'enabled'

    Scrape_Data['ups_list'][0]['variables'].append( {'name': 'ups.beeper.status', 'value': BeepState} )
    Scrape_Data['ups_list'][0]['variables'].append( {'name': 'ups.beeper.status.text', 'value': BeepStateText} )
    return

#===========================================================
# UPS_Status
#===========================================================
def UPS_Status( Scrape_Data ):
# ITEMP
# Internal UPS temperature as supplied by the UPS.
# STATUS
# The current status of the UPS (ONLINE, ONBATT, etc.)
# STATFLAG
# Status flag. English version is given by STATUS.

    ITemp = ''
    ITEMP = format_to_text.Get_NUT_Variable( Scrape_Data['ups_list'][0], 'ITEMP' )
    if ITEMP:
        ITemp = str(Strip_Numeric( ITEMP ))
    Scrape_Data['ups_list'][0]['variables'].append( {'name': 'ups.temperature', 'value': ITemp} )

    Status_Word = 0
    STATFLAG = format_to_text.Get_NUT_Variable( Scrape_Data['ups_list'][0], 'STATFLAG' )
    if STATFLAG:
        Status_Word = Strip_Hex( STATFLAG )

    Status_List = []
    for Define in Constants_STATFLAG:
        if (Define['Mask'] & Status_Word) != 0:
            current_app.logger.debugvv("Found: {} {}".format( Define['Define'], Define['Status'] ))
            if Define['Status'] not in Status_List:
                Status_List.append( Define['Status'] )

    Status_String = ""
    for s in Status_List:
        Status_String += s + " "

    Scrape_Data['ups_list'][0]['variables'].append( {'name': 'ups.status', 'value': Status_String.strip()} )
    return

#===========================================================
# Output_Power
#===========================================================
def Output_Power( Scrape_Data ):
# NOMPOWER
# The maximum power in Watts that the UPS is designed to supply.
# LOADPCT
# The percentage of load capacity as estimated by the UPS.
    LoadPct = '0'
    NomPower = '0'

    LOADPCT = format_to_text.Get_NUT_Variable( Scrape_Data['ups_list'][0], 'LOADPCT' )
    if LOADPCT:
        LoadPct = str(Strip_Numeric( LOADPCT ))

    NOMPOWER = format_to_text.Get_NUT_Variable( Scrape_Data['ups_list'][0], 'NOMPOWER' )
    if NOMPOWER:
        NomPower = str(Strip_Numeric( NOMPOWER ))

    Scrape_Data['ups_list'][0]['variables'].append( {'name': 'ups.load', 'value': LoadPct} )
    Scrape_Data['ups_list'][0]['variables'].append( {'name': 'ups.realpower.nominal', 'value': NomPower} )
    return

#===========================================================
# Input_Voltage
#===========================================================
def Input_Voltage( Scrape_Data ):
# LINEV
# The current line voltage as returned by the UPS.    
# NOMINV
# The input voltage that the UPS is configured to expect.
# NOMOUTV
# The output voltage that the UPS will attempt to supply when on battery power.
# LOTRANS
# The line voltage below which the UPS will switch to batteries.
# HITRANS
# The line voltage above which the UPS will switch to batteries.
# OUTPUTV
# The voltage the UPS is supplying to your equipment
    LineV = '0'
    OutputV = '0'
    NomV = '0'
    LowTrans = '0'
    HiTrans = '0'

    #=======================================================
    # Input (LINEV) and output (OUTPUTV) voltages
    #=======================================================
    LINEV = format_to_text.Get_NUT_Variable( Scrape_Data['ups_list'][0], 'LINEV' )
    if LINEV:
        LineV = str(Strip_Numeric( LINEV ))
    Scrape_Data['ups_list'][0]['variables'].append( {'name': 'input.voltage', 'value': LineV} )

    OUTPUTV = format_to_text.Get_NUT_Variable( Scrape_Data['ups_list'][0], 'OUTPUTV' )
    if OUTPUTV:
        OutputV = str(Strip_Numeric( OUTPUTV ))
    Scrape_Data['ups_list'][0]['variables'].append( {'name': 'output.voltage', 'value': OutputV} )

    #=======================================================
    # NOMINV Takes priority over NOMOUTV, however for some
    #   models these parameters may be mutually exclusive?
    #=======================================================
    NOMOUTV = format_to_text.Get_NUT_Variable( Scrape_Data['ups_list'][0], 'NOMOUTV' )
    if NOMOUTV:
        NomV = str(Strip_Numeric( NOMOUTV ))
    NOMINV = format_to_text.Get_NUT_Variable( Scrape_Data['ups_list'][0], 'NOMINV' )
    if NOMINV:
        NomV = str(Strip_Numeric( NOMINV ))
    Scrape_Data['ups_list'][0]['variables'].append( {'name': 'input.voltage.nominal', 'value': NomV} )

    #=======================================================
    # Transition values LOTRANS & HITRANS
    #=======================================================
    LOTRANS = format_to_text.Get_NUT_Variable( Scrape_Data['ups_list'][0], 'LOTRANS' )
    if LOTRANS:
        LowTrans = str(Strip_Numeric( LOTRANS ))
    HITRANS = format_to_text.Get_NUT_Variable( Scrape_Data['ups_list'][0], 'HITRANS' )
    if HITRANS:
        HiTrans = str(Strip_Numeric( HITRANS ))

    Scrape_Data['ups_list'][0]['variables'].append( {'name': 'input.transfer.low', 'value': LowTrans} )
    Scrape_Data['ups_list'][0]['variables'].append( {'name': 'input.transfer.high', 'value': HiTrans} )

    return

#===========================================================
# Battery_Voltage
#===========================================================
def Battery_Voltage( Scrape_Data ):
# BATTV
# Battery voltage as supplied by the UPS.
# NOMBATTV
# The nominal battery voltage.
    BattV = '0'
    NomBattV = '0'
    Batt_Low_Volt = '0'

    BATTV = format_to_text.Get_NUT_Variable( Scrape_Data['ups_list'][0], 'BATTV' )
    if BATTV:
        BattV = str(Strip_Numeric( BATTV ))
    Scrape_Data['ups_list'][0]['variables'].append( {'name': 'battery.voltage', 'value': BattV} )

    NOMBATTV = format_to_text.Get_NUT_Variable( Scrape_Data['ups_list'][0], 'NOMBATTV' )
    if NOMBATTV:
        NomBattV = str(Strip_Numeric( NOMBATTV ))
    Scrape_Data['ups_list'][0]['variables'].append( {'name': 'battery.voltage.nominal', 'value': NomBattV} )

    Batt_Low_Volt = str( float(NomBattV) * 0.87 )
    Scrape_Data['ups_list'][0]['variables'].append( {'name': 'battery.voltage.low', 'value': Batt_Low_Volt} )

    return

#===========================================================
# Battery_Charge
#===========================================================
def Battery_Charge( Scrape_Data ):
# MBATTCHG
# If the battery charge percentage (BCHARGE) drops below this
# BCHARGE
# The percentage charge on the batteries.
    BCharge = '0'
    MBattChg = '0'

    BCHARGE = format_to_text.Get_NUT_Variable( Scrape_Data['ups_list'][0], 'BCHARGE' )
    MBATTCHG = format_to_text.Get_NUT_Variable( Scrape_Data['ups_list'][0], 'MBATTCHG' )
    if BCHARGE:
        BCharge = str(Strip_Numeric( BCHARGE ))
    if MBATTCHG:
        MBattChg = str(Strip_Numeric( MBATTCHG ))

    Scrape_Data['ups_list'][0]['variables'].append( {'name': 'battery.charge', 'value': BCharge} )
    Scrape_Data['ups_list'][0]['variables'].append( {'name': 'battery.charge.low', 'value': MBattChg} )
    Scrape_Data['ups_list'][0]['variables'].append( {'name': 'battery.charge.warning', 'value': MBattChg} )

    return

#===========================================================
# Battery_Runtime
#===========================================================
def Battery_Runtime( Scrape_Data ):
# DLOWBATT
# The remaining runtime below which the UPS sends the low battery signal. At this point apcupsd will
# force an immediate emergency shutdown.
# MINTIMEL
# apcupsd will shutdown your system if the remaining runtime equals or is below this point. Value is set
# in the configuration file (MINUTES)
# TIMELEFT
# The remaining runtime left on batteries as estimated by the UPS.
    # DLowBatt = '0'
    MinTimeL = '0'
    TimeLeft = '0'

    TIMELEFT = format_to_text.Get_NUT_Variable( Scrape_Data['ups_list'][0], 'TIMELEFT' )
    if TIMELEFT:
        TimeLeft = str(int(Strip_Numeric( TIMELEFT ) * 60 ))
    Scrape_Data['ups_list'][0]['variables'].append( {'name': 'battery.runtime', 'value': TimeLeft} )    

    MINTIMEL = format_to_text.Get_NUT_Variable( Scrape_Data['ups_list'][0], 'MINTIMEL' )
    if MINTIMEL:
        MinTimeL = str(Strip_Numeric( MINTIMEL ) * 60 )
    Scrape_Data['ups_list'][0]['variables'].append( {'name': 'battery.runtime.low', 'value': MinTimeL} )
    return

#===========================================================
# Translate_APC_To_NUT
#===========================================================
def Translate_APC_To_NUT( Scrape_Data ):
    Battery_Charge( Scrape_Data )
    Battery_Voltage( Scrape_Data )
    Input_Voltage( Scrape_Data )
    Output_Power( Scrape_Data )
    Battery_Runtime( Scrape_Data )
    UPS_Status( Scrape_Data )
    Beeper_Status( Scrape_Data )
    Time_Controls( Scrape_Data )
    Other_Parameters( Scrape_Data )
                     
    current_app.logger.debug("Translate_APC_To_NUT: Transformed Scrape_Data {}".format( Scrape_Data ))

    return
