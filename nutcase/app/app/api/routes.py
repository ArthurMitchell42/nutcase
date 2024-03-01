from flask import current_app, request

from app.api import bp

from app.utils import scrape
from app.utils import gui_data_format

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
