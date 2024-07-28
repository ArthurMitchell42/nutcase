from datetime import datetime, timedelta
from flask import current_app

from app import db
from app.models import LogEntry, Log_Level

from sqlalchemy import and_

# =================================================================================================
# Scan_DB - Periodically go though the DB and update the config events icon values
# =================================================================================================
def Scan_DB(app):
    with app.app_context():
        Filters = [LogEntry.read == False, LogEntry.level == Log_Level.info.value]  # noqa: E712
        Active_Logs = LogEntry.query.filter(and_(*Filters))
        app.config['APP_STATUS_FLAGS']['info'] = Active_Logs.count()

        Filters = [LogEntry.read == False, LogEntry.level == Log_Level.warning.value]  # noqa: E712
        Active_Logs = LogEntry.query.filter(and_(*Filters))
        app.config['APP_STATUS_FLAGS']['warning'] = Active_Logs.count()

        Filters = [LogEntry.read == False, LogEntry.level == Log_Level.alert.value]  # noqa: E712
        Active_Logs = LogEntry.query.filter(and_(*Filters))
        app.config['APP_STATUS_FLAGS']['alert'] = Active_Logs.count()

# =================================================================================================
# Scan_DB_For_Device - Go though the DB for a specific device
# =================================================================================================
def Scan_DB_For_Device(Server, Device):
    Filters = [LogEntry.server == Server, LogEntry.device == Device]  # noqa: E712
    Active_Logs = LogEntry.query.filter(and_(*Filters)).all()

    Log_Values = {}
    Log_Values['info'] = Log_Values['warning'] = Log_Values['alert'] = 0
    Log_Values['info_unread'] = Log_Values['warning_unread'] = Log_Values['alert_unread'] = 0
    for log in Active_Logs:
        if log.level == Log_Level.info.value:
            Log_Values['info'] += 1
            if not log.read:
                Log_Values['info_unread'] += 1
        elif log.level == Log_Level.warning.value:
            Log_Values['warning'] += 1
            if not log.read:
                Log_Values['warning_unread'] += 1
        elif log.level == Log_Level.alert.value:
            Log_Values['alert'] += 1
            if not log.read:
                Log_Values['alert_unread'] += 1
    return Log_Values

# =================================================================================================
# Scan_DB_For_Server - Go though the DB for a specific server
# =================================================================================================
def Scan_DB_For_Server(Server):
    Filters = [LogEntry.server == Server, LogEntry.device == ""]  # noqa: E712
    Active_Logs = LogEntry.query.filter(and_(*Filters)).all()

    Log_Values = {}
    Log_Values['info'] = Log_Values['warning'] = Log_Values['alert'] = 0
    Log_Values['info_unread'] = Log_Values['warning_unread'] = Log_Values['alert_unread'] = 0
    for log in Active_Logs:
        if log.level == Log_Level.info.value:
            Log_Values['info'] += 1
            if not log.read:
                Log_Values['info_unread'] += 1
        elif log.level == Log_Level.warning.value:
            Log_Values['warning'] += 1
            if not log.read:
                Log_Values['warning_unread'] += 1
        elif log.level == Log_Level.alert.value:
            Log_Values['alert'] += 1
            if not log.read:
                Log_Values['alert_unread'] += 1
    return Log_Values

# =================================================================================================
# Clean_Old_Logs - Go though the DB and remove old or over length logs
# =================================================================================================
def Clean_Old_Logs(Retention_Days):
    Expiry_Time = datetime.now() - timedelta(days=Retention_Days + 1)
    Log_Time = LogEntry.time_latest

    Filters = [Log_Time < Expiry_Time]
    Target_Logs = LogEntry.query.filter(and_(*Filters))
    Count = Target_Logs.delete()
    try:
        if Count > 0:
            db.session.commit()
    except Exception:
        Count = 0
        current_app.logger.error("Error deleting logs")

    current_app.logger.info("Tidying logs, deleted {}".format(Count))
