import logging
import re
import json

from enum import Enum
from http.server import BaseHTTPRequestHandler, HTTPServer
from http import HTTPStatus
from urllib.parse import urlparse
from urllib.parse import parse_qs
from ipaddress import ip_address    # For parsing target addresses

import server_constants
import nut_server_handler
import apc_server_handler
import format_to_text
import format_to_json
import globals

#=======================================================================
# Connect to the app log
#=======================================================================
log = logging.getLogger('__main__.' + __name__)

#=======================================================================
# Enumerated types
#=======================================================================
Server_Protocol = Enum('Server_Protocol', ['NUT', 'APC', 'NONE'])

#=======================================================================
# Utility to print the last n lines of a log file
#=======================================================================
def Tail_File( File_Name, Display_Lines=20):
    Lines = []
    First_Line = '<pre><span style="{}">'.format(server_constants.Monospace_Small_Font)
    Last_Line  = '</span"></pre>'

    try:
        File_Handle = open( File_Name, 'r')

        Log_Pattern = re.compile("^([0-9-]+) ([0-9:,]+) (DEBUG|INFO|WARNING|ERROR|CRITICAL|FATAL) (.+)$")
        count = 0

        while True:
            count += 1
            line = File_Handle.readline()
            if not line:
                break
            line = line.rstrip("\n")
            match = re.search(Log_Pattern, line)
            if match:
                if   match.group(3) == "DEBUG":     Level_Colour = server_constants.HTML_Colour_Green
                elif match.group(3) == "INFO":      Level_Colour = server_constants.HTML_Colour_LightBlue
                elif match.group(3) == "WARNING":   Level_Colour = server_constants.HTML_Colour_Yellow
                elif match.group(3) == "ERROR":     Level_Colour = server_constants.HTML_Colour_Red
                elif match.group(3) == "CRITICAL":  Level_Colour = server_constants.HTML_Colour_DarkRed
                elif match.group(3) == "FATAL":     Level_Colour = server_constants.HTML_Colour_DarkRed
                else:                               Level_Colour = server_constants.HTML_Colour_Blue

                line = '{date} {time} <span style="{lstyle}">{level}</span> {message}<br>'.format( 
                                date   = match.group(1),
                                time   = match.group(2),
                                lstyle = Level_Colour,
                                level  = match.group(3),
                                message= match.group(4)
                                )

            Lines.append( line )
            if len(Lines) > Display_Lines:
                Lines.pop(0)
        Result = [ First_Line ] + Lines + [ Last_Line ]
    except Exception as Error:
        log.warning( "Could not open log file to serve it: {}".format(globals.Log_File) ) 
        Lines.append( "<p>Could not open log file: {}</p>".format( globals.Log_File ) )
        return False, Lines
    
    return True, Result

#====================================================================================================
# The web server end point handlers
#====================================================================================================
# Send_Text_Reply
#====================================================================================================
def Send_Text_Reply( Channel, Scrape_Data ):
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
# Send_Object_As_JSON
#=======================================================================
def Send_Object_As_JSON( Channel, Data_Object, Response_Message ):    
    Formatted_JSON_Text = json.dumps(Data_Object)

    Channel.send_response(code=200, message=Response_Message)
    Channel.send_header(keyword='Content-type', value=server_constants.Content_Types["json"])
    Channel.end_headers()
    Channel.wfile.write(Formatted_JSON_Text.encode('utf-8'))
    return

#====================================================================================================
# Send_Not_Found - If an error occurs while scraping the NUT server
#====================================================================================================
def Send_HTML_Reply( Channel, Control ):
    Channel.send_response( Control["code"], Control["message"] )
    Channel.send_header(keyword='Content-type', value=server_constants.Content_Types["html"])
    Channel.end_headers()

    Channel.wfile.write(bytes("<html><head><title>" + Control["title"] + "</title></head>", "utf-8"))
    Channel.wfile.write(bytes("<body " + server_constants.Main_Font + ">", "utf-8"))

    for Line in Control["lines"]:
        Channel.wfile.write(bytes( Line, "utf-8") )

    Channel.wfile.write(bytes("</body></html>", "utf-8"))
    return

#====================================================================================================
# Utility to parse and validate the target IP and port
#====================================================================================================
def Validate_Target( Target_Param ):
    Target_Address = "" 
    Parameter_Target_Port = None

    Addr, Separator, Port = Target_Param.rpartition(':')

    if not Separator:
        Addr, Port = Port, None

    try:
        Target_Address = str(ip_address(Addr))
    except ValueError as Error:
        log.error("Improper IP address for target {}".format(Target_Address))
        return False, None, None

    if Port: 
        if Port.isnumeric():
            Parameter_Target_Port = int(Port)
        else:
            log.error("Improper port for target {}".format(Port))
            return False, Target_Address, None

    return True, Target_Address, Parameter_Target_Port

#====================================================================================================
# Resolve the target server addrees and, optionally, port
#====================================================================================================
def Resolve_Address_And_Port( params ):
    Target_Resolved = False
    Target_Address  = None
    Parameter_Port = None

    if "target" in params:
        rtn, Target_Address, Parameter_Port = Validate_Target(params["target"][0])
        if rtn:
            Target_Resolved = True
    elif "addr" in params:
        try:
            Target_Address = str(ip_address(params["addr"][0]))
            Target_Resolved = True
        except ValueError as Error:
            log.error("Improper IP address for target {}".format(params["addr"]))

    if "port" in params:
        if params["port"][0].isnumeric():
            Parameter_Port = params["port"][0]
        else:
            log.error("Improper port specified {}".format( params["port"] ))
            Target_Resolved = False

    return Target_Resolved, Target_Address, Parameter_Port

#====================================================================================================
# The web server class and functions
#====================================================================================================
class NUTCaseServer(BaseHTTPRequestHandler):
    def do_GET(self):
        Request_Path = self.path
        Parsed_Path = urlparse(Request_Path)
        URL_Parameters = parse_qs(Parsed_Path.query)

        if globals.Log_Request_Debug:
            log.debug( "request_path: {}".format(Request_Path) ) 
            log.debug( "self.headers:" )
            message = ""
            for h in  self.headers:
                message += h + " -> " + self.headers[h] + '\n'
            log.debug( message ) 
            log.debug( "parsed_path: {}".format(Parsed_Path) ) 
            log.debug( "params: " ) 
            message = ""
            for k in URL_Parameters:
                message += k + " -> " + URL_Parameters[k][0] + '\n'
            log.debug( message ) 

            message = '\n'.join([
                'CLIENT VALUES:',
                'client_address=%s (%s)' % (self.client_address,
                    self.address_string()),
                'command=%s' % self.command,
                'path=%s' % self.path,
                'real path=%s' % Parsed_Path.path,
                'query=%s' % Parsed_Path.query,
                'request_version=%s' % self.request_version,
                'SERVER VALUES:',
                'server_version=%s' % self.server_version,
                'sys_version=%s' % self.sys_version,
                'protocol_version=%s' % self.protocol_version,
                ])
            log.debug( "Dump of self attributes: {}".format(message) ) 

        #============================================================================================
        # Check the mode (NUT or APC) from the URL parameters
        #============================================================================================
        Server_Type = Server_Protocol.NUT
        Target_Port = 3493         # Default NUT port, may be overridden below by parameters
        if "mode" in URL_Parameters:
            if URL_Parameters["mode"][0].lower() == "nut":
                Server_Type = Server_Protocol.NUT
                Target_Port = 3493
            elif URL_Parameters["mode"][0].lower() == "apc":
                Server_Type = Server_Protocol.APC
                Target_Port = 3551 # Default APC port, may be overridden below by parameters
            else:
                Server_Type = Server_Protocol.NONE
                log.error("Unknown server mode requested: {}".format( URL_Parameters["mode"][0] ))
                Lines = [ "<pre>Unknown server mode requested: <b>{}</b></pre>".format( URL_Parameters["mode"][0] ) ]
                Lines += server_constants.HTML_Usage

                Control = { "code": HTTPStatus.NOT_FOUND, 
                            "message": HTTPStatus.NOT_FOUND.phrase,
                            "title": HTTPStatus.NOT_FOUND.phrase,
                            "lines": Lines
                            }
                Send_HTML_Reply( self, Control )
                return

        #============================================================================================
        # Route to a responder based on the end point path
        #============================================================================================
        if Parsed_Path.path == "/log":
            Log_Lines = globals.Default_Log_Lines
            if "lines" in URL_Parameters:
                Log_Lines = int(URL_Parameters["lines"][0])

            rtn, Lines = Tail_File( globals.Log_File, Log_Lines )
            
            if rtn: Control = { "code": HTTPStatus.OK,        "title": "Log file" }
            else:   Control = { "code": HTTPStatus.NOT_FOUND, "title": "Error - log file" }
            Control["message"] = "Log file"
            Control["lines"]   = Lines
            Send_HTML_Reply( self, Control )
        elif Parsed_Path.path == "/help" or Parsed_Path.path == "/" :
            Control = { "code": HTTPStatus.OK, 
                        "message": "Usage",
                        "title": "Usage",
                        "lines": server_constants.HTML_Usage
                        }
            Send_HTML_Reply( self, Control )
        elif Parsed_Path.path == "/health":
            Health_Check = { "OK": "true" }
            Response_Message = "Health check"
            Send_Object_As_JSON( self, Health_Check, Response_Message )
        else:
            if Parsed_Path.path == "/metrics" or \
               Parsed_Path.path == "/json"    or \
               Parsed_Path.path == "/raw"     or \
               Parsed_Path.path == "/apclog":

                #====================================================================================
                # Get the target address and, optionally port, from the URL parameters
                #====================================================================================
                Target_Resolved, Target_Address, Parameter_Port = Resolve_Address_And_Port( URL_Parameters )
                if Parameter_Port:
                    Target_Port = Parameter_Port
 
                if not Target_Resolved:
                    Lines = [ "<pre>Target address not resolved: <b>{}</b></pre>".format( URL_Parameters ) ]
                    Lines += server_constants.HTML_Usage

                    Control = { "code": HTTPStatus.NOT_FOUND, 
                                "message": HTTPStatus.NOT_FOUND.phrase,
                                "title": HTTPStatus.NOT_FOUND.phrase,
                                "lines": Lines
                                }
                    Send_HTML_Reply( self, Control )
                    log.warning('Target address not resolved, returned 404: {}'.format(Parsed_Path.path) ) 
                    return

                if Parsed_Path.path == "/apclog":
                    Log_Lines = apc_server_handler.Get_APC_Log(Target_Address, Target_Port)
                    Response_Message = "Data"
                    Send_Object_As_JSON( self, Log_Lines, Response_Message )
                    return

                if Server_Type == Server_Protocol.NUT:
                    Scrape_Return, Scrape_Data = nut_server_handler.Scrape_NUT_Server( Target_Address, Target_Port )
                elif Server_Type == Server_Protocol.APC:
                    Scrape_Return, Scrape_Data = apc_server_handler.Scrape_APC_Server( Target_Address, Target_Port )

                if not Scrape_Return:
                    Control = { "code": HTTPStatus.NOT_FOUND, 
                                "message": HTTPStatus.NOT_FOUND.phrase,
                                "title": HTTPStatus.NOT_FOUND.phrase,
                                "lines": [ "<pre>Not found</pre>" ]
                                }
                    Send_HTML_Reply( self, Control )
                    return

                if Parsed_Path.path == "/metrics":
                    Send_Text_Reply( self, Scrape_Data )
                elif Parsed_Path.path == "/json":
                    Formatted_JSON_Object = format_to_json.Format_For_JSON( Scrape_Data )
                    Response_Message = "Data"
                    Send_Object_As_JSON( self, Formatted_JSON_Object, Response_Message )
                elif Parsed_Path.path == "/raw":
                    Response_Message = "Data"
                    Send_Object_As_JSON( self, Scrape_Data, Response_Message )
            else:
                Lines = [ "<pre>Path not found: <b>{}</b></pre>".format( Parsed_Path.path ) ]
                Lines += server_constants.HTML_Usage

                Control = { "code": HTTPStatus.NOT_FOUND, 
                            "message": HTTPStatus.NOT_FOUND.phrase,
                            "title": HTTPStatus.NOT_FOUND.phrase,
                            "lines": Lines
                            }
                Send_HTML_Reply( self, Control )
                log.warning('Returned 404: {}'.format(Parsed_Path.path) ) 
        return
    
    def log_message(self, format, *args):
        if globals.Log_Requests:
            log.info("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format%args))
        return

#====================================================================================================
# Launch the web browser
#====================================================================================================
def Launch_HTTP_Server( Server_Port ):
    NUTCase_WebServer = HTTPServer(('', Server_Port), NUTCaseServer)
    log.info( "Server starting on port {}".format( Server_Port ) ) 

    try:
        NUTCase_WebServer.serve_forever()
    except (KeyboardInterrupt):
        log.info("User terminated program")
    except Exception as Error:
        log.error("HTTP Server terminated: {}".format( Error ))

    log.info( "Server stopped" ) 
    return
