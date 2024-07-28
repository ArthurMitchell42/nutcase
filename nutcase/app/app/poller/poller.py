import sqlalchemy as sa
from datetime import datetime, timezone
import time
from flask import current_app

from app.cache_controller.cache_controller import Scrape_Bucket

from app import db
from app.models import LogEntry, Log_Level, Log_Category

from app.utils.format_to_text import Get_NUT_Variable
from enum import Enum

from app.utils import configuration

Log_Type = Enum("Log_Type", ["single", "recuring", "discreate"])

# =================================================================================================
# region Log handling
# Log_Event_Message
# =================================================================================================
def Log_Event_Message(Log_Info):
    assert "title" in Log_Info
    assert "detail" in Log_Info
    assert "category" in Log_Info
    assert "level" in Log_Info

    if "server" not in Log_Info:
        Log_Info['server'] = None
    if "type" not in Log_Info:
        Log_Info['type'] = Log_Type.discreate

    Title = Log_Info['title'].format(
                            server=Log_Info['server'],
                            category=Log_Info['category'])
    Detail = Log_Info['detail'].format(
                            server=Log_Info['server'],
                            category=Log_Info['category'])

    if Log_Info['type'] == Log_Type.recuring or Log_Info['type'] == Log_Type.single:
        Old_Log = db.session.scalar(sa.select(LogEntry).where(
                    (LogEntry.title  == Title) &
                    (LogEntry.detail == Detail) &
                    (LogEntry.server == Log_Info['server']) &
                    (LogEntry.device == Log_Info['device']) &
                    (LogEntry.read == False)  # noqa: E712
                    ))

        if Old_Log:
            if Log_Info['type'] == Log_Type.recuring:
                Old_Log.occurrences += 1
                Old_Log.read = False
            Old_Log.time_latest = datetime.now(timezone.utc)
        else:
            New_Log = LogEntry(title   = Title,
                                detail  = Detail,
                                category= Log_Info['category'],
                                server  = Log_Info['server'],
                                device  = Log_Info['device'],
                                level   = Log_Info['level'].value)
            db.session.add(New_Log)
    elif Log_Info['type'] == Log_Type.discreate:
        New_Log = LogEntry(title=Title,
                            detail=Detail,
                            server=Log_Info['server'],
                            device  = Log_Info['device'],
                            category=Log_Info['category'],
                            level=Log_Info['level'].value)
        db.session.add(New_Log)

    db.session.commit()
    return

# =================================================================================================
# Log_Comms_Issue
# =================================================================================================
def Log_Comms_Issue(Server_Info):
    Log_Info = {}
    Log_Info['title'] = "Server connection"
    Log_Info['detail'] = "Server {} port {}, mode {} could not be accessed".format(
                            Server_Info['server'],
                            Server_Info['port'],
                            Server_Info['mode'])
    Log_Info['server'] = Server_Info['server']
    Log_Info['device'] = ""
    Log_Info['category'] = Log_Category.Comms.name
    Log_Info['level'] = Log_Level.warning
    Log_Info['type'] = Log_Type.recuring

    Log_Event_Message(Log_Info)
    return

# =================================================================================================
# Log_Comms_Issue
# =================================================================================================
def Log_Scrape_Issue(Server_Info):
    Log_Info = {}
    Log_Info['title'] = "Poll duration"
    Log_Info['detail'] = "Server {} port {}, mode {} exceded the processing time limit".format(
                            Server_Info['server'],
                            Server_Info['port'],
                            Server_Info['mode'])
    Log_Info['server'] = Server_Info['server']
    Log_Info['device'] = ""
    Log_Info['category'] = Log_Category.Comms.name
    Log_Info['level'] = Log_Level.alert
    Log_Info['type'] = Log_Type.recuring

    Log_Event_Message(Log_Info)
    return

Device_State_Cache = {}

# =============================================================================================
# region Check parameters
# Check_Status - Check status key-words changing
# =============================================================================================
def Check_Status(Previous_Data, Current_Data):
    Log_Info = {}
    Log_Info['type'] = Log_Type.discreate
    if "OB" in Current_Data['ups.status'] and "OB" not in Previous_Data['ups.status']:
        Log_Info['title'] = "UPS On battery"
        Log_Info['detail'] = "Device {} on server {} went on to battery.".format(
                                Current_Data['device'], Current_Data['server_address'])
        Log_Info['server'] = Current_Data['server_address']
        Log_Info['device'] = Current_Data['device']
        Log_Info['category'] = Log_Category.Power.name
        Log_Info['level'] = Log_Level.alert
        Log_Event_Message(Log_Info)
    if "OL" in Current_Data['ups.status'] and "OL" not in Previous_Data['ups.status']:
        Log_Info['title'] = "Power restored"
        Log_Info['detail'] = "Device {} on server {} went back on power.".format(
                                Current_Data['device'], Current_Data['server_address'])
        Log_Info['server'] = Current_Data['server_address']
        Log_Info['device'] = Current_Data['device']
        Log_Info['category'] = Log_Category.Power.name
        Log_Info['level'] = Log_Level.info
        Log_Event_Message(Log_Info)
    if "RB" in Current_Data['ups.status']:
        Log_Info['title'] = "Replace battery"
        Log_Info['detail'] = "Device {} on server {} declared 'replace battery'.".format(
                                Current_Data['device'], Current_Data['server_address'])
        Log_Info['server'] = Current_Data['server_address']
        Log_Info['device'] = Current_Data['device']
        Log_Info['category'] = Log_Category.Power.name
        Log_Info['level'] = Log_Level.alert
        Log_Info['type'] = Log_Type.single
        Log_Event_Message(Log_Info)
    if "CHRG" in Current_Data['ups.status'] and "CHRG" not in Previous_Data['ups.status']:
        Log_Info['title'] = "Charging started"
        Log_Info['detail'] = "Device {} on server {} started to charge.".format(
                                Current_Data['device'], Current_Data['server_address'])
        Log_Info['server'] = Current_Data['server_address']
        Log_Info['device'] = Current_Data['device']
        Log_Info['category'] = Log_Category.Battery.name
        Log_Info['level'] = Log_Level.info
        Log_Event_Message(Log_Info)
    if "CHRG" not in Current_Data['ups.status'] and "CHRG" in Previous_Data['ups.status']:
        Log_Info['title'] = "Charging stopped"
        Log_Info['detail'] = "Device {} on server {} stopped charging.".format(
                                Current_Data['device'], Current_Data['server_address'])
        Log_Info['server'] = Current_Data['server_address']
        Log_Info['device'] = Current_Data['device']
        Log_Info['category'] = Log_Category.Battery.name
        Log_Info['level'] = Log_Level.info
        Log_Event_Message(Log_Info)
    if "LB" in Current_Data['ups.status'] and "LB" not in Previous_Data['ups.status']:
        Log_Info['title'] = "Low battery"
        Log_Info['detail'] = "Device {} on server {} declared low battery.".format(
                                Current_Data['device'], Current_Data['server_address'])
        Log_Info['server'] = Current_Data['server_address']
        Log_Info['device'] = Current_Data['device']
        Log_Info['category'] = Log_Category.Battery.name
        Log_Info['level'] = Log_Level.warning
        Log_Event_Message(Log_Info)
    if "SD" in Current_Data['ups.status'] and "SD" not in Previous_Data['ups.status']:
        Log_Info['title'] = "Shutdown"
        Log_Info['detail'] = "Device {} on server {} declared shutdown.".format(
                                Current_Data['device'], Current_Data['server_address'])
        Log_Info['server'] = Current_Data['server_address']
        Log_Info['device'] = Current_Data['device']
        Log_Info['category'] = Log_Category.Power.name
        Log_Info['level'] = Log_Level.warning
        Log_Event_Message(Log_Info)
    if "FSD" in Current_Data['ups.status'] and "FSD" not in Previous_Data['ups.status']:
        Log_Info['title'] = "Forced shutdown"
        Log_Info['detail'] = "Device {} on server {} declared forced shutdown.".format(
                                Current_Data['device'], Current_Data['server_address'])
        Log_Info['server'] = Current_Data['server_address']
        Log_Info['device'] = Current_Data['device']
        Log_Info['category'] = Log_Category.Power.name
        Log_Info['level'] = Log_Level.alert
        Log_Event_Message(Log_Info)
    if "BYPASS" in Current_Data['ups.status'] and "BYPASS" not in Previous_Data['ups.status']:
        Log_Info['title'] = "On bypass"
        Log_Info['detail'] = "Device {} on server {} went into bypass.".format(
                                Current_Data['device'], Current_Data['server_address'])
        Log_Info['server'] = Current_Data['server_address']
        Log_Info['device'] = Current_Data['device']
        Log_Info['category'] = Log_Category.Power.name
        Log_Info['level'] = Log_Level.warning
        Log_Event_Message(Log_Info)
    if "BYPASS" not in Current_Data['ups.status'] and "BYPASS" in Previous_Data['ups.status']:
        Log_Info['title'] = "Off bypass"
        Log_Info['detail'] = "Device {} on server {} came out of bypass.".format(
                                Current_Data['device'], Current_Data['server_address'])
        Log_Info['server'] = Current_Data['server_address']
        Log_Info['device'] = Current_Data['device']
        Log_Info['category'] = Log_Category.Power.name
        Log_Info['level'] = Log_Level.info
        Log_Event_Message(Log_Info)
    if "TRIM" in Current_Data['ups.status'] and "TRIM" not in Previous_Data['ups.status']:
        Log_Info['title'] = "Triming"
        Log_Info['detail'] = "Device {} on server {} trimmed the input voltage.".format(
                                Current_Data['device'], Current_Data['server_address'])
        Log_Info['server'] = Current_Data['server_address']
        Log_Info['device'] = Current_Data['device']
        Log_Info['category'] = Log_Category.Power.name
        Log_Info['level'] = Log_Level.warning
        Log_Event_Message(Log_Info)
    if "TRIM" not in Current_Data['ups.status'] and "TRIM" in Previous_Data['ups.status']:
        Log_Info['title'] = "Stopped triming"
        Log_Info['detail'] = "Device {} on server {} stopped trimmed the input voltage.".format(
                                Current_Data['device'], Current_Data['server_address'])
        Log_Info['server'] = Current_Data['server_address']
        Log_Info['device'] = Current_Data['device']
        Log_Info['category'] = Log_Category.Power.name
        Log_Info['level'] = Log_Level.info
        Log_Event_Message(Log_Info)
    if "BOOST" in Current_Data['ups.status'] and "BOOST" not in Previous_Data['ups.status']:
        Log_Info['title'] = "Boosting"
        Log_Info['detail'] = "Device {} on server {} boosted the input voltage.".format(
                                Current_Data['device'], Current_Data['server_address'])
        Log_Info['server'] = Current_Data['server_address']
        Log_Info['device'] = Current_Data['device']
        Log_Info['category'] = Log_Category.Power.name
        Log_Info['level'] = Log_Level.warning
        Log_Event_Message(Log_Info)
    if "BOOST" not in Current_Data['ups.status'] and "BOOST" in Previous_Data['ups.status']:
        Log_Info['title'] = "Stopped boosting"
        Log_Info['detail'] = "Device {} on server {} stopped boosting the input voltage.".format(
                                Current_Data['device'], Current_Data['server_address'])
        Log_Info['server'] = Current_Data['server_address']
        Log_Info['device'] = Current_Data['device']
        Log_Info['category'] = Log_Category.Power.name
        Log_Info['level'] = Log_Level.info
        Log_Event_Message(Log_Info)
    return

# =============================================================================================
# Check_Charge - Log changes in the battery charge
# =============================================================================================
def Check_Charge(Previous_Data, Current_Data):
    Delta = (int(Current_Data['battery.charge']) - Previous_Data['last_rep_ch'])

    Last_Rep = Previous_Data['last_rep_ch']
    if abs(Delta) >= current_app.config['REPORT_BAT_CHARGE_PC'] or \
            (Last_Rep < 100 and int(Current_Data['battery.charge']) == 100):
        if Last_Rep != Current_Data['battery.charge']:
            Previous_Data['last_rep_ch'] = Current_Data['battery.charge']

        Log_Info = {}
        if Delta < 0:
            Log_Info['title'] = "Battery charge"
            Log_Info['detail'] = "Server {}, device {} charge {}%".format(
                                    Current_Data['server_address'],
                                    Current_Data['device'],
                                    Current_Data['battery.charge'])
            Log_Info['server'] = Current_Data['server_address']
            Log_Info['device'] = Current_Data['device']
            Log_Info['category'] = Log_Category.Battery.name
            Log_Info['level'] = Log_Level.warning
            Log_Info['type'] = Log_Type.discreate
            Log_Event_Message(Log_Info)
        else:
            Log_Info['title'] = "Battery charge"
            Log_Info['detail'] = "Server {}, device {} charge {}%".format(
                                    Current_Data['server_address'],
                                    Current_Data['device'],
                                    Current_Data['battery.charge'])
            Log_Info['server'] = Current_Data['server_address']
            Log_Info['device'] = Current_Data['device']
            Log_Info['category'] = Log_Category.Battery.name
            Log_Info['level'] = Log_Level.info
            Log_Info['type'] = Log_Type.discreate
            Log_Event_Message(Log_Info)
    return

# =============================================================================================
# Check_Runtime - Log changes in the run time
# =============================================================================================
def Check_Runtime(Previous_Data, Current_Data):
    if Current_Data['battery.charge'] > 98:
        return

    Delta = (int(Current_Data['battery.runtime']) - Previous_Data['last_rep_rt'])

    Last_Rep = Previous_Data['last_rep_rt']
    if abs(Delta) >= current_app.config['REPORT_BAT_RUNTIME_S']:
        if Last_Rep != Current_Data['battery.runtime']:
            Previous_Data['last_rep_rt'] = Current_Data['battery.runtime']

        Log_Info = {}

        if Delta < 0:
            Log_Info['title'] = "Battery runtime"
            Log_Info['detail'] = "Server {}, device {} runtime {}s".format(
                                    Current_Data['server_address'],
                                    Current_Data['device'],
                                    Current_Data['battery.runtime'])
            Log_Info['server'] = Current_Data['server_address']
            Log_Info['device'] = Current_Data['device']
            Log_Info['category'] = Log_Category.Battery.name
            Log_Info['level'] = Log_Level.warning
            Log_Info['type'] = Log_Type.discreate
            Log_Event_Message(Log_Info)
        else:
            Log_Info['title'] = "Battery runtime"
            Log_Info['detail'] = "Server {}, device {} runtime {}s".format(
                                    Current_Data['server_address'],
                                    Current_Data['device'],
                                    Current_Data['battery.runtime'])
            Log_Info['server'] = Current_Data['server_address']
            Log_Info['device'] = Current_Data['device']
            Log_Info['category'] = Log_Category.Battery.name
            Log_Info['level'] = Log_Level.info
            Log_Info['type'] = Log_Type.discreate
            Log_Event_Message(Log_Info)
    return

# =================================================================================================
# Check_Device_Clients
# =================================================================================================
def Check_Device_Clients(Expected_Clients, Device_Data):
    for expected in Expected_Clients:
        if expected not in Device_Data['clients']:
            Log_Info = {}
            Log_Info['title'] = "Missing client"
            Log_Info['detail'] = "Device {} on server {} is missing client {}".format(
                                Device_Data['name'], Device_Data['server_address'], expected)
            Log_Info['server'] = Device_Data['server_address']
            Log_Info['device'] = Device_Data['name']
            Log_Info['category'] = Log_Category.Other.name
            Log_Info['level'] = Log_Level.alert
            Log_Info['type'] = Log_Type.recuring
            Log_Event_Message(Log_Info)
    return

# =================================================================================================
# region Check_Device_Parameters
# =================================================================================================
def Check_Device_Parameters(Device_Data):
    Handle = Device_Data['server_address'] + "_" + Device_Data['name']

    Current_Data = {}
    Current_Data['server_address'] = Device_Data['server_address']
    Current_Data['device'] = Device_Data['name']
    Current_Data['ups.status'] = Get_NUT_Variable(Device_Data, 'ups.status')
    ch = Get_NUT_Variable(Device_Data, 'battery.charge')
    if ch:
        Current_Data['battery.charge'] = int(ch)
    else:
        Current_Data['battery.charge'] = None

    rt = Get_NUT_Variable(Device_Data, 'battery.runtime')
    if rt:
        Current_Data['battery.runtime'] = int(rt)
    else:
        Current_Data['battery.runtime'] = None

    Current_Data['server_address'] = Device_Data['server_address']
    Current_Data['device'] = Device_Data['name']

    if Handle not in Device_State_Cache:
        Device_State_Cache[Handle] = Current_Data
        Device_State_Cache[Handle]['last_rep_ch'] = Current_Data['battery.charge']
        Device_State_Cache[Handle]['last_rep_rt'] = Current_Data['battery.runtime']
        Device_State_Cache[Handle]['battery.charge'] = Current_Data['battery.charge']
        Device_State_Cache[Handle]['battery.runtime'] = Current_Data['battery.runtime']
        Device_State_Cache[Handle]['starting'] = True

    Previous_Data = Device_State_Cache[Handle]

    if Current_Data['ups.status']:
        Check_Status(Previous_Data, Current_Data)

    # If clients are listed, check them
    Device = configuration.Get_Device(Device_Data['server_address'],
                                                    Device_Data['name'])
    if Device:
        if 'clients' in Device:
            Check_Device_Clients(Device['clients'], Device_Data)

    if Current_Data['battery.charge']:
        Check_Charge(Previous_Data, Current_Data)
    Current_Data['last_rep_ch'] = Previous_Data['last_rep_ch']

    if Current_Data['battery.runtime']:
        Check_Runtime(Previous_Data, Current_Data)
    Current_Data['last_rep_rt'] = Previous_Data['last_rep_rt']

    Device_State_Cache[Handle] = Current_Data
    Device_State_Cache[Handle]['starting'] = False
    return

# =================================================================================================
# region Server_Poll
# Periodically scrape all listed servers
# =================================================================================================
def Server_Poll(app):
    with app.app_context():
        for s in current_app.config['SERVERS']:
            Start_Time = time.time()

            # Don't poll a server if monitor is false
            if 'monitor' in s:
                if s['monitor'] is False:
                    continue

            Bucket = Scrape_Bucket(s['server'], s['port'], s['mode'])
            current_app.config['CACHE_QUEUE'].put(Bucket)
            ready_flag = Bucket.get_flag()
            ready_flag.acquire()
            Ready = ready_flag.wait(timeout=current_app.config['SCRAPE_TIMEOUT'])
            # Check time out
            if not Ready:
                ready_flag.release()
                continue
            ready_flag.release()

            Aquire_Time = time.time() - Start_Time
            # Check if the scrape failed
            if not Bucket.result:
                Log_Comms_Issue(s)
            else:
                for dev in Bucket.scrape_data['ups_list']:
                    Check_Device_Parameters(dev)

            Process_Time = (time.time() - Start_Time) - Aquire_Time
            current_app.logger.debug(f"Aquire {Aquire_Time} Process {Process_Time} "
                            "Total {Process_Time + Aquire_Time}")
            if (Process_Time + Aquire_Time) > current_app.config['REPORT_SCRAPE_LIMIT']:
                current_app.logger.warning(f"Server {s['server']} Aquire {Aquire_Time} "
                                "Process {Process_Time} Total {Process_Time+Aquire_Time}")
                Log_Scrape_Issue(s)
    return
