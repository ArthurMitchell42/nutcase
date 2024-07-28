from flask import current_app, render_template, request, Response, send_from_directory, flash
from markupsafe import Markup       # For building tables
from app.main import bp

from http import HTTPStatus         # For responses
import json
import os
import datetime

from app.utils import server_constants
from app.utils import format_to_text
from app.utils import format_to_json
from app.utils import apc_server_handler
from app.utils import configuration
from app.utils import scrape
from app.utils import file_utils
from app.utils import gui_data_format

# =======================================================================
# before_app_request - Run before every request to check config file
# =======================================================================
@bp.before_app_request
def before_request():
    if configuration.Config_File_Modified():
        configuration.Load_Config()
        current_app.logger.info("Reloading configuration.")
    return

# ====================================================================================
# Serve the end-point /
# ====================================================================================
@bp.route('/')
def route_index():
    # TODO - reduce logging levels
    for a in request.args:
        current_app.logger.debugv("request.args: key {} value {}".format(a, request.args[a]))
    return render_template('main/index.html', title='Dashboard')

# ====================================================================================
# Serve the end-point /raw
# ====================================================================================
@bp.route('/raw')
def route_raw():
    Scrape_Return, Scrape_Data = scrape.Get_Scrape_Data(dict(request.args))
    if not Scrape_Return:
        r = Response(response=HTTPStatus.NOT_FOUND.phrase, status=HTTPStatus.NOT_FOUND)
        return r

    if request.args.get("download") == 'true':
        Formatted_JSON_Text = json.dumps(Scrape_Data, indent=2)
        r = Response(response=Formatted_JSON_Text, mimetype=server_constants.Content_Types["text"])
        Server = Scrape_Data['server_address']
        Device = Scrape_Data['ups_list'][0]['name']
        Timestamp = datetime.datetime.now().strftime(
            current_app.config['DOWNLOAD_TIMESTAMP_FORMAT'])
        Filename = "Raw_JSON_{svr}_{dev}_{ts}.txt".format(svr=Server, dev=Device, ts=Timestamp)
        r.headers["Content-disposition"] = 'attachment; filename={}'.format(Filename)
        return r

    Formatted_JSON_Text = json.dumps(Scrape_Data)
    Content_Type = server_constants.Content_Types["json"]
    r = Response(response=Formatted_JSON_Text, status=HTTPStatus.OK, mimetype=Content_Type)
    return r

# ====================================================================================
# Serve the end-point /json
# ====================================================================================
@bp.route('/json')
def route_json():
    Scrape_Return, Scrape_Data = scrape.Get_Scrape_Data(dict(request.args))
    if not Scrape_Return:
        r = Response(response=HTTPStatus.NOT_FOUND.phrase, status=HTTPStatus.NOT_FOUND)
        return r

    JSON_Elements = request.args.getlist("elem")
    current_app.logger.debugv("JSON_Elements: {}".format(JSON_Elements))

    Formatted_JSON_Object = format_to_json.Format_For_JSON(Scrape_Data, JSON_Elements)

    if request.args.get("download") == 'true':
        Formatted_JSON_Text = json.dumps(Formatted_JSON_Object, indent=2)
        r = Response(response=Formatted_JSON_Text,
                     mimetype=server_constants.Content_Types["text"])

        Server = Scrape_Data['server_address']
        Device = Scrape_Data['ups_list'][0]['name']
        Timestamp = datetime.datetime.now().strftime(
            current_app.config['DOWNLOAD_TIMESTAMP_FORMAT'])

        Filename = "JSON_{svr}_{dev}_{ts}.txt".format(svr=Server, dev=Device, ts=Timestamp)
        r.headers["Content-disposition"] = 'attachment; filename={}'.format(Filename)
        return r

    Formatted_JSON_Text = json.dumps(Formatted_JSON_Object)
    Content_Type = server_constants.Content_Types["json"]
    r = Response(response=Formatted_JSON_Text, status=HTTPStatus.OK, mimetype=Content_Type)
    return r

# ====================================================================================
# Serve the end-point /metrics
# ====================================================================================
@bp.route('/metrics')
def route_metrics():
    Scrape_Return, Scrape_Data = scrape.Get_Scrape_Data(dict(request.args))
    if not Scrape_Return:
        r = Response(response=HTTPStatus.NOT_FOUND.phrase, status=HTTPStatus.NOT_FOUND)
        return r

    Formatted_Data = format_to_text.Format_For_Prometheus(Scrape_Data)

    if request.args.get("download") == 'true':
        r = Response(response=Formatted_Data, mimetype=server_constants.Content_Types["text"])
        Server = Scrape_Data['server_address']
        Device = Scrape_Data['ups_list'][0]['name']
        Timestamp = datetime.datetime.now().strftime(
                        current_app.config['DOWNLOAD_TIMESTAMP_FORMAT'])

        Filename = "Metrics_{svr}_{dev}_{ts}.txt".format(svr=Server, dev=Device, ts=Timestamp)
        r.headers["Content-disposition"] = 'attachment; filename={}'.format(Filename)
        return r

    Accept_Header = request.headers.get('accept')
    current_app.logger.debugv("Accept_Header: {}".format(Accept_Header))

    Content_Type = server_constants.Content_Types["text"]
    if server_constants.Accepts_Openmetrics in Accept_Header:
        Content_Type = server_constants.Content_Types["openmetrics"]

    r = Response(response=Formatted_Data, status=HTTPStatus.OK, mimetype=Content_Type)
    r.headers["Content-Type"] = Content_Type
    return r

# ====================================================================================
# Serve the end-point /log
# ====================================================================================
@bp.route('/log')
@bp.route('/log/<Filename>')
def route_log(Filename=''):
    if Filename == '':
        Filename = current_app.config['LOGFILE_NAME']
    if '../' in Filename or Filename[:1] == '/':
        Filename = current_app.config['LOGFILE_NAME']

    # Get the number of lines requested
    Log_Lines = current_app.config["DEFAULT_LOG_LINES"]
    if Lines := request.args.get("lines"):
        try:
            Log_Lines = int(Lines)
            flash('Set lines to {}'.format(Log_Lines), "text-white bg-success")
        except Exception:
            current_app.logger.error("Error defining log lines: {}".format(Lines))

    # Generate the HTML for the list of files
    Logfile_Directory = os.path.join(current_app.config['CONFIG_PATH'],
                                     current_app.config['LOGFILE_SUBPATH'])
    Logfile_Fullname = os.path.join(Logfile_Directory, Filename)

    File_List = gui_data_format.Generate_Log_Files_Pulldown(Logfile_Directory)

    # Get lines from the requested log file
    rtn, Lines = file_utils.Tail_File(Logfile_Fullname, Log_Lines)
    if not rtn:
        Lines = ["<pre>Log file not found</pre>"]

    return render_template('main/log.html', title="Log file",
                           lines=Lines, files=Markup(File_List), filename=Filename)

# ====================================================================================
# Serve the end-point /help
# ====================================================================================
@bp.route('/help')
def route_help():
    return render_template('main/help.html', title="Help")

# ====================================================================================
# Serve the end-point /health
# ====================================================================================
@bp.route('/health')
def route_health():
    Health = {"OK": "true"}
    Formatted_JSON_Text = json.dumps(Health)
    Content_Type = server_constants.Content_Types["json"]
    r = Response(response=Formatted_JSON_Text, status=HTTPStatus.OK, mimetype=Content_Type)
    return r

# ====================================================================================
# Serve the end-point /apclog
# ====================================================================================
@bp.route('/apclog')
def route_apclog():
    URL_Parameters = dict(request.args)

    Server_Type, Target_Port = scrape.Check_Mode(URL_Parameters)

    if not Server_Type:
        r = Response(response=HTTPStatus.NOT_FOUND.phrase, status=HTTPStatus.NOT_FOUND)
        return r

    Target_Resolved, Target_Address, Parameter_Port \
                        = scrape.Resolve_Address_And_Port(URL_Parameters)
    if Parameter_Port:
        Target_Port = Parameter_Port

    if not Target_Resolved:
        r = Response(response=HTTPStatus.NOT_FOUND.phrase, status=HTTPStatus.NOT_FOUND)
        return r

    Log_Lines = apc_server_handler.Get_APC_Log(Target_Address, Target_Port)
    return render_template('main/apclog.html', lines=Log_Lines)

# ====================================================================================
# Serve the end-point /download
# ====================================================================================
@bp.route('/download', methods=['GET', 'POST'])
@bp.route('/download/<path:Filename>', methods=['GET', 'POST'])
def route_download(Filename=None):
    if not Filename:
        r = Response(response=HTTPStatus.NOT_FOUND.phrase, status=HTTPStatus.NOT_FOUND)
        return r

    Download_Path = os.path.join(current_app.config['CONFIG_PATH'],
                                 current_app.config['LOGFILE_SUBPATH'])
    return send_from_directory(Download_Path, Filename)
