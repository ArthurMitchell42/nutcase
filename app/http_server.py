import logging
import re
import json

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from urllib.parse import parse_qs

from ipaddress import ip_address # For parsing targhet addresses

import server_constants
import nut_server_handler
import format_to_text
import format_to_json

from nutcase import Log_File_Name, Log_Requests, Log_Request_Debug

log = logging.getLogger('__main__.' + __name__)

#=======================================================================
# Utility to print the last n lines of a log file
#=======================================================================
def tail(f, Display_Lines=20):
    Log_Pattern = re.compile("^([0-9-]+) ([0-9:,]+) (DEBUG|INFO|WARNING|ERROR|CRITICAL|FATAL) (.+)$")
    count = 0
    Result = ""
    Lines = []

    while True:
        count += 1
         # Get next line from file
        line = f.readline()
        # if line is empty end of file is reached
        if not line:
            break

        match = re.search(Log_Pattern, line)
        if match:
            if   match.group(3) == "DEBUG":     Level_Colour = server_constants.HTML_Colour_Green
            elif match.group(3) == "INFO":      Level_Colour = server_constants.HTML_Colour_LightBlue
            elif match.group(3) == "WARNING":   Level_Colour = server_constants.HTML_Colour_Yellow
            elif match.group(3) == "ERROR":     Level_Colour = server_constants.HTML_Colour_Red
            elif match.group(3) == "CRITICAL":  Level_Colour = server_constants.HTML_Colour_DarkRed
            elif match.group(3) == "FATAL":     Level_Colour = server_constants.HTML_Colour_DarkRed
            else:                               Level_Colour = server_constants.HTML_Colour_Blue
            line = match.group(1) + match.group(2) + "<span " + Level_Colour + "> " + match.group(3) + "</span>" + "<span " + server_constants.HTML_Colour_Blue + "> " + match.group(4) + "</span>"

        Lines.append( line )
        if len(Lines) > Display_Lines:
            Lines.pop(0)

    for l in Lines:
        Result += l + "<br>"

    return Result

#====================================================================================================
# Send_Not_Found - If an error occurs while scraping the NUT server
#====================================================================================================
def Send_Not_Found( Channel ):
        Channel.send_response(404)
        Channel.send_header(keyword='Content-type', value=server_constants.Content_Types["html"])
        Channel.end_headers()

        Channel.wfile.write(bytes("<html><head><title>Not found</title></head>", "utf-8"))
        Channel.wfile.write(bytes("<body " + server_constants.Main_Font + ">", "utf-8"))
        Channel.wfile.write(bytes("<pre>Not found</pre>", "utf-8"))
        Channel.wfile.write(bytes("</body></html>", "utf-8"))
        return

#====================================================================================================
# The web server end point handlers
#====================================================================================================
# Send_Text_Reply
#====================================================================================================
def Send_Text_Reply( Channel, Data ):

    Scrape_Return, Scrape_Data = nut_server_handler.Scrape_Server( Data["Target_Address"], Data["Target_Port"] )
    if not Scrape_Return:
        Send_Not_Found( Channel )
        return

    Formatted_Data = format_to_text.Format_For_Prometheus( Scrape_Data )

    Content_Type = server_constants.Content_Types["text"]
    if server_constants.Accepts_Openmetrics in Channel.headers["Accept"]:
        Content_Type = server_constants.Content_Types["openmetrics"]

    Channel.send_response(200)
    Channel.send_header(keyword='Content-type', value=Content_Type)
    Channel.end_headers()

    Channel.wfile.write(bytes(Formatted_Data, "utf-8"))
    return

#=======================================================================
# Send_JSON_Reply
#=======================================================================
def Send_JSON_Reply( Channel, Data ):

    Scrape_Return, Scrape_Data = nut_server_handler.Scrape_Server( Data["Target_Address"], Data["Target_Port"] )
    if not Scrape_Return:
        Send_Not_Found( Channel )
        return
    
    # Formatted_JSON_Text = json.dumps(Data)
    # Formatted_JSON_Text = json.dumps(Scrape_Data)
    Formatted_JSON_Text = format_to_json.Format_To_JSON( Scrape_Data )

    Channel.send_response(code=200, message='Here is your data')
    Channel.send_header(keyword='Content-type', value=server_constants.Content_Types["json"])
    Channel.end_headers()
    Channel.wfile.write(Formatted_JSON_Text.encode('utf-8'))
    return

#=======================================================================
# Send_Raw_JSON_Reply
#=======================================================================
def Send_Raw_JSON_Reply( Channel, Data ):
    Scrape_Return, Scrape_Data = nut_server_handler.Scrape_Server( Data["Target_Address"], Data["Target_Port"] )
    if not Scrape_Return:
        Send_Not_Found( Channel )
        return
    
    Formatted_JSON_Text = json.dumps(Scrape_Data)

    Channel.send_response(code=200, message='Here is your data')
    Channel.send_header(keyword='Content-type', value=server_constants.Content_Types["json"])
    Channel.end_headers()
    Channel.wfile.write(Formatted_JSON_Text.encode('utf-8'))
    return

#=======================================================================
# Send_Error_Reply
#=======================================================================
def Send_Usage_Reply( Channel, Error_404 ):

    if Error_404:
        Channel.send_response(404)
    else:
        Channel.send_response(200)

    Channel.send_header(keyword="Content-type", value=server_constants.Content_Types["html"])
    Channel.end_headers()

    if Error_404:
        Channel.wfile.write(bytes("<html><head><title>Not found</title></head>", "utf-8"))
    else:
        Channel.wfile.write(bytes("<html><head><title>Usage</title></head>", "utf-8"))

    Channel.wfile.write(bytes("<body " + server_constants.Main_Font + ">", "utf-8"))

    if Error_404:
        Channel.wfile.write(bytes("<p>Requested path not found: %s</p>" % urlparse(Channel.path).path, "utf-8"))
        
    Channel.wfile.write(bytes("<p>Default paths are:</p>", "utf-8"))

    Channel.wfile.write(bytes("<pre><span "+server_constants.HTML_Colour_Green+">", "utf-8"))
    Channel.wfile.write(bytes("<span "+server_constants.Monospace_Font+"><b>For text output compatible with Prometheus scraping.</b><br>", "utf-8"))
    Channel.wfile.write(bytes("</span><span "+server_constants.HTML_Colour_Blue+">", "utf-8"))
    Channel.wfile.write(bytes("<span "+server_constants.Monospace_Font+"><b>/metrics?target=A.B.C.D</b></span>       Specifying the address of the server, assuming the default port, 3493.<br>", "utf-8"))
    Channel.wfile.write(bytes("<span "+server_constants.Monospace_Font+"><b>/metrics?target=A.B.C.D%3aP</b></span>  Specifying the address of the server and the port.<br>", "utf-8"))
    Channel.wfile.write(bytes("<span "+server_constants.Monospace_Font+"><b>/metrics?addr=A.B.C.D&port=P</b></span> Specifying the address of the server and the port (P).<br>", "utf-8"))
    Channel.wfile.write(bytes("<span "+server_constants.Monospace_Font+"><br>", "utf-8"))

    Channel.wfile.write(bytes("<span "+server_constants.HTML_Colour_Green+">", "utf-8"))
    Channel.wfile.write(bytes("<span "+server_constants.Monospace_Font+"><b>For JSON output compatible with HomePage and Webhooks.</b><br>", "utf-8"))
    Channel.wfile.write(bytes("</span><span "+server_constants.HTML_Colour_Blue+">", "utf-8"))
    Channel.wfile.write(bytes("<span "+server_constants.Monospace_Font+"><b>/json?target=A.B.C.D</b></span>      Specifying the address of the server, assuming the default port, 3493.<br>", "utf-8"))
    Channel.wfile.write(bytes("<span "+server_constants.Monospace_Font+"><b>/json?target=A.B.C.D%3aP</b></span>  Specifying the address of the server and the port.<br>", "utf-8"))
    Channel.wfile.write(bytes("<span "+server_constants.Monospace_Font+"><b>/json?addr=A.B.C.D&port=P</b></span> Specifying the address of the server and the port (P).<br>", "utf-8"))
    Channel.wfile.write(bytes("<span "+server_constants.Monospace_Font+"><br>", "utf-8"))

    Channel.wfile.write(bytes("<span "+server_constants.HTML_Colour_Green+">", "utf-8"))
    Channel.wfile.write(bytes("<span "+server_constants.Monospace_Font+"><b>Raw JSON containg all, unprocessed, data recieved from the NUT server.</b><br>", "utf-8"))
    Channel.wfile.write(bytes("</span><span "+server_constants.HTML_Colour_Blue+">", "utf-8"))
    Channel.wfile.write(bytes("<span "+server_constants.Monospace_Font+"><b>/raw?target=A.B.C.D</b></span>      Specifying the address of the server, assuming the default port, 3493.<br>", "utf-8"))
    Channel.wfile.write(bytes("<span "+server_constants.Monospace_Font+"><b>/raw?target=A.B.C.D%3aP</b></span>  Specifying the address of the server and the port.<br>", "utf-8"))
    Channel.wfile.write(bytes("<span "+server_constants.Monospace_Font+"><b>/raw?addr=A.B.C.D&port=P</b></span> Specifying the address of the server and the port (P).<br>", "utf-8"))
    Channel.wfile.write(bytes("<span "+server_constants.Monospace_Font+"><br>", "utf-8"))

    Channel.wfile.write(bytes("<span "+server_constants.HTML_Colour_Green+">", "utf-8"))
    Channel.wfile.write(bytes("<span "+server_constants.Monospace_Font+"><b>View the log file.</b><br>", "utf-8"))
    Channel.wfile.write(bytes("</span><span "+server_constants.HTML_Colour_Blue+">", "utf-8"))
    Channel.wfile.write(bytes("<span "+server_constants.Monospace_Font+"><b>/log</b></span>          View the last 20 lines of the log file.<br>", "utf-8"))
    Channel.wfile.write(bytes("<span "+server_constants.Monospace_Font+"><b>/log?lines=30</b></span> Optionally view a set number of last lines of the log file.<br>", "utf-8"))
    Channel.wfile.write(bytes("<span "+server_constants.Monospace_Font+"><br>", "utf-8"))

    Channel.wfile.write(bytes("<span "+server_constants.HTML_Colour_Green+">", "utf-8"))
    Channel.wfile.write(bytes("<span "+server_constants.Monospace_Font+"><b>For example, if your NUT server is at 10.0.20.50, serving on the default port (3493) and nutcase is on address 10.0,20.40 on the default port (9995) then to get data for Prometheus enter:</b><br>", "utf-8"))
    Channel.wfile.write(bytes("</span><span "+server_constants.HTML_Colour_Blue+">", "utf-8"))
    Channel.wfile.write(bytes("<span "+server_constants.Monospace_Font+"><p style='margin-left: 20px;'><b>http://10.0.20.40:9995/metrics?target=10.0.20.50%3a3493</b></span></p>", "utf-8"))
    Channel.wfile.write(bytes("</span></pre>", "utf-8"))

    Channel.wfile.write(bytes("<p>For details go to <a href='https://github.com/ArthurMitchell42/nutcase'>NUTCase on GitHub</a></p>", "utf-8"))

    Channel.wfile.write(bytes("</body></html>", "utf-8"))
    return

#=======================================================================
# Send_Log_Reply
#=======================================================================
def Send_Log_Reply( Channel, Data ):
    Log_Lines = 20
    if "lines" in Data:
        Log_Lines = int(Data["lines"][0])

    try:
        File_Handle = open( Log_File_Name, 'r')
        Channel.send_response(200)
        Channel.send_header(keyword="Content-type", value=server_constants.Content_Types["html"])
        Channel.end_headers()
        Channel.wfile.write(bytes("<html><head><title>Log file</title></head>", "utf-8"))
        Channel.wfile.write(bytes("<body " + server_constants.Main_Font + ">", "utf-8"))
        Channel.wfile.write(bytes("<p>Log file entries. This may take some time for a large log file.</p>", "utf-8"))

        message = tail(File_Handle, Log_Lines)
        Channel.wfile.write(bytes("<span " + server_constants.Monospace_Font + ">", "utf-8"))
        Channel.wfile.write(bytes(message, "utf-8"))
        Channel.wfile.write(bytes("</span>", "utf-8"))

        Channel.wfile.write(bytes("</body></html>", "utf-8"))

        File_Handle.close()
    except Exception as Error:
        log.warning( "Could not open log file to serve it: {}".format(Log_File_Name) ) 
        Channel.send_response(404)
        Channel.send_header(keyword="Content-type", value=server_constants.Content_Types["html"])
        Channel.end_headers()
        Channel.wfile.write(bytes("<html><head><title>Log file error</title></head>", "utf-8"))
        Channel.wfile.write(bytes("<body>", "utf-8"))
        Channel.wfile.write(bytes("<p>Could not open log file: %s</p>" % Log_File_Name, "utf-8"))
        Channel.wfile.write(bytes("</body></html>", "utf-8"))
    return

#====================================================================================================
# Utility to parse and validate the target IP and port
#====================================================================================================
def Validate_Target( Param ):
    Target_Port = 3493
    Target_Address = "0.0.0.0"

    Addr, Separator, Port = Param.rpartition(':')

    if Separator:
        if Port: 
            if Port.isnumeric():
                Target_Port = int(Port) # convert to integer
            else:
                log.error("Improper port for target {}".format(Port))
                return False, Target_Address, Target_Port
        else:    
            Target_Port = 3493
    else:
        Target_Port  = 3493
        Addr         = Port
    
    try:
        Target_Address = ip_address(Addr)
    except ValueError as Error:
        Target_Address = ip_address("0.0.0.0")
        log.error("Improper IP address for target {}".format(Target_Address))
        return False, Target_Address, Target_Port

    return True, Target_Address, Target_Port

#====================================================================================================
# The web server class and functions
#====================================================================================================
class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        request_path = self.path
        parsed_path = urlparse(request_path)
        params = parse_qs(parsed_path.query)

        if Log_Request_Debug:
            log.debug( "request_path: {}".format(request_path) ) 
            log.debug( "self.headers:" )
            message = ""
            for h in  self.headers:
                message += h + " -> " + self.headers[h] + '\n'
            log.debug( message ) 
            log.debug( "parsed_path: {}".format(parsed_path) ) 
            log.debug( "params: " ) 
            message = ""
            for k in params:
                message += k + " -> " + params[k][0] + '\n'
            log.debug( message ) 

            message = '\n'.join([
                'CLIENT VALUES:',
                'client_address=%s (%s)' % (self.client_address,
                    self.address_string()),
                'command=%s' % self.command,
                'path=%s' % self.path,
                'real path=%s' % parsed_path.path,
                'query=%s' % parsed_path.query,
                'request_version=%s' % self.request_version,
                'SERVER VALUES:',
                'server_version=%s' % self.server_version,
                'sys_version=%s' % self.sys_version,
                'protocol_version=%s' % self.protocol_version,
                ])
            log.debug( "Dump of self attributes: {}".format(message) ) 

        #============================================================================================
        # Get the target address and, optionally port, from the URL parameters
        #============================================================================================
        Target_Resolved = False
        Target_Address  = ""
        Target_Port     = 3493 # The default NUT server port number, may be overridden by parameters
        if "target" in params:
            rtn, Target_Address, Target_Port = Validate_Target(params["target"][0])
            if rtn:
                Target_Resolved = True
        elif "addr" in params:
            try:
                Target_Address = ip_address(params["addr"][0])
                Target_Resolved = True
            except ValueError as Error:
                log.error("Improper IP address for target {}".format(Target_Address))
                Target_Resolved = False

            if "port" in params:
                if params["port"][0].isnumeric():
                    Target_Port = params["port"][0]
                else:
                    Target_Resolved = False

        params["Target_Address"] = str(Target_Address)
        params["Target_Port"] = Target_Port

        if parsed_path.path == "/metrics":
            if Target_Resolved:
                Send_Text_Reply( self, params )
            else:
                Send_Usage_Reply( self, True )
                log.warning('Target not sent, returned 404: {}'.format(parsed_path.path) ) 
        elif parsed_path.path == "/json":
            if Target_Resolved:
                Send_JSON_Reply( self, params )
            else:
                Send_Usage_Reply( self, True )
                log.warning('Target not sent, returned 404: {}'.format(parsed_path.path) ) 
        elif parsed_path.path == "/raw":
            if Target_Resolved:
                Send_Raw_JSON_Reply( self, params )
            else:
                Send_Usage_Reply( self, True )
                log.warning('Target not sent, returned 404: {}'.format(parsed_path.path) ) 
        elif parsed_path.path == "/log":
            Send_Log_Reply( self, params )
        elif parsed_path.path == "/help":
            Send_Usage_Reply( self, False )
        else:
            Send_Usage_Reply( self, True )
            log.warning('Returned 404: {}'.format(parsed_path.path) ) 

    def log_message(self, format, *args):
        if Log_Requests:
            log.info("%s - - [%s] %s\n" % (self.address_string(),self.log_date_time_string(),format%args))
        return

#====================================================================================================
# Launch the web browser
#====================================================================================================
def Launch_HTTP_Server( ServerPort ):
    webServer = HTTPServer(('', ServerPort), MyServer)
    log.info( "Server starting on port %s" % (ServerPort) ) 

    try:
        webServer.serve_forever()
    except (KeyboardInterrupt):
        log.info("User terminated program")
    except Exception as Error:
        log.error("HTTP Server terminated: {}".format( Error ))

    log.info( "Server stopped" ) 

    return
