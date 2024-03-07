from flask import current_app, request

from app.api import bp

from app.utils import scrape
from app.utils import gui_data_format
from app.api import api_utils

# ====================================================================================
# Serve the end-point /api/status
# ====================================================================================
@bp.route('/status')
def route_status():
    Result = {}

    Args = dict(request.args)

    Device = request.args.get('dev')
    if not Device:
        current_app.logger.debug("No device in args")
        return Result

    Scrape_Return, Scrape_Data = scrape.Get_Scrape_Data(Args)
    if not Scrape_Return:
        current_app.logger.debug("No scrape data")
        return Result

    Result = gui_data_format.Process_Data_For_GUI(Scrape_Data, Device)
    return Result

# ====================================================================================
# Serve the end-point /api/status
# ====================================================================================
@bp.route('/devices')
def route_devices():
    Result = {}
    Device = request.args.get('dev')
    Addr   = request.args.get('addr')

    Result = gui_data_format.Process_Device_Pulldown(Addr, Device, Result)
    return Result

# ====================================================================================
# Serve the end-point /api/default - Returns JSON for the default (or last) server
#   in the config file server section.
# ====================================================================================
@bp.route('/default')
def route_default():
    Result = {}

    if len(current_app.config['SERVERS']) == 0:
        return Result

    for s in current_app.config['SERVERS']:
        Result['addr']   = s['server']
        Result['port']   = s['port']
        Result['device'] = s['device']
        if 'default' in s:
            break

    return Result

# ====================================================================================
# Serve the end-point /api/events - Returns JSON for the event icons
#   on the tool bar.
# ====================================================================================
@bp.route('/events')
def route_events():
    Result = {}
    Overflow = "99+"
    if current_app.config['APP_STATUS_FLAGS']['info'] > 100:
        Result['info_flag_val'] = Overflow
    elif current_app.config['APP_STATUS_FLAGS']['info'] > 0:
        Result['info_flag_val'] = str(current_app.config['APP_STATUS_FLAGS']['info'])
    else:
        Result['info_flag_val'] = ""
    if current_app.config['APP_STATUS_FLAGS']['warning'] > 100:
        Result['warn_flag_val'] = Overflow
    elif current_app.config['APP_STATUS_FLAGS']['warning'] > 0:
        Result['warn_flag_val'] = str(current_app.config['APP_STATUS_FLAGS']['warning'])
    else:
        Result['warn_flag_val'] = ""
    if current_app.config['APP_STATUS_FLAGS']['alert'] > 100:
        Result['alert_flag_val'] = Overflow
    elif current_app.config['APP_STATUS_FLAGS']['alert'] > 0:
        Result['alert_flag_val'] = str(current_app.config['APP_STATUS_FLAGS']['alert'])
    else:
        Result['alert_flag_val'] = ""

    return Result

# ====================================================================================
# Serve the end-point /api/events - Returns JSON for the event icons
#   on the tool bar.
# ====================================================================================
@bp.route('/appupdate')
def route_appupdate():
    Result = {}

    Result['app_update'] = api_utils.Get_Update_String()

    return Result
