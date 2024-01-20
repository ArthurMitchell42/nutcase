from flask import current_app

import re
import socket
from enum import Enum

from app.api import rework_data

#=======================================================================
# Enumerated types
#=======================================================================
NUT_Query_List_State = Enum('NUT_Query_List_State', ['INITIAL', 'STARTED', 'ENDED', 'MALFORMED', 'ERROR'])

#=======================================================================
# Read server respose
#=======================================================================
def Parse_Server_Response( Socket_File, Request, UPSs, Debug_Lines ):
    Begin_Pattern       = re.compile(r"^BEGIN " + Request.decode() + "$")
    End_Pattern         = re.compile(r"^END " + Request.decode() + "$")
    Error_Pattern       = re.compile(r"^ERR (.+)$")
    UPS_Pattern         = re.compile(r'^UPS (.+?) (.*)$')
    VAR_Pattern         = re.compile(r'^VAR (.+?) (.+?) (.*)$')
    UPS_Client_Pattern  = re.compile(r'^CLIENT (.+?) (.*)$')

    List_State = NUT_Query_List_State.INITIAL

    try:
        while True:
            Line = Socket_File.readline().decode()
            if Line[-1] == "\n":
                Line = Line[:-1]
            Debug_Lines.append(Line)

            if re.search( Error_Pattern, Line ):
                List_State = NUT_Query_List_State.ERROR
                break
            else:
                # State machine
                # Look for first line
                if List_State == NUT_Query_List_State.INITIAL:
                    if re.search( Begin_Pattern, Line ):
                        List_State = NUT_Query_List_State.STARTED
                    else:
                        List_State = NUT_Query_List_State.ERROR
                        break
                elif List_State == NUT_Query_List_State.STARTED:
                    if re.search( End_Pattern, Line ):
                        List_State = NUT_Query_List_State.ENDED
                        break
                    else: # => NUT_Query_List_State.STARTED
                        ups_match = re.search( UPS_Pattern, Line )
                        var_match = re.search( VAR_Pattern, Line )
                        client_match = re.search( UPS_Client_Pattern, Line )
                        if ups_match:
                            UPS = { 
                                "name": ups_match.group(1),
                                "description": ups_match.group(2).strip("\""),
                                "variables": [],
                                "clients": []
                            }
                            UPSs.append( UPS )
                        elif var_match:
                            VAR = {
                                "name": var_match.group(2),
                                "value": var_match.group(3).strip("\"")
                            }

                            for i in UPSs:
                                if i["name"] == var_match.group(1):
                                    # log.debug( "Found UPS {} for VAR {}".format( var_match.group(1), var_match.group(2) ) )
                                    i["variables"].append(VAR)
                        elif client_match:
                            Client = {
                                "upsname": client_match.group(1),
                                "client": client_match.group(2)
                            }
                            current_app.logger.debugv( "Client match {} for UPS {}".format( Client["client"], Client["upsname"] ) )

                            for i in UPSs:
                                if i["name"] == client_match.group(1):
                                    # log.debug( "Found UPS {} for VAR {}".format( var_match.group(1), var_match.group(2) ) )
                                    i["clients"].append(Client["client"])
                        else:
                            List_State = NUT_Query_List_State.MALFORMED
                            break
    except Exception as Error:
        current_app.logger.error( "Error scraping server: {}".format(Error) )
        return False
    
    if List_State == NUT_Query_List_State.MALFORMED:
        current_app.logger.error( "Malformed response from server: {}".format(Line) ) 
        return False
    if List_State == NUT_Query_List_State.ERROR:
        current_app.logger.error( "Error from server: {}".format(Line) ) 
        return False
    
    current_app.logger.debug( "List_State {}".format( List_State ) ) 

    return True

#=======================================================================
# Query_NUT_Version
#=======================================================================
def Query_NUT_Version( Socket, Socket_File, Debug_Lines ):
    Error_Pattern = re.compile(r"^ERR (.+)$")
    Version_Pattern = re.compile(r"^(.+) upsd (.+) - (.+)$")

    Request = b"VER\n"
    Socket_File.write(Request)
    Debug_Lines.append(Request.decode())

    data = Socket_File.readline()
    Version_Line = data.decode()
    Debug_Lines.append(Version_Line)

    if Version_Line[-1] == "\n":
        Version_Line = Version_Line[:-1]

    match = re.search(Error_Pattern, Version_Line)
    if match:
        current_app.logger.error( "The NUT server returned an error when asked for its version: {}".format( Version_Line ) )
        if match.group(1) == "ACCESS-DENIED":
            IPAddr = Socket.getsockname()[0]
            current_app.logger.error( "ACCESS-DENIED may mean the NUT server has not had my IP address ({}) added to its allowed list.".format( IPAddr ) )
        return False, ""

    match = re.search(Version_Pattern, Version_Line)
    if match:
        NUT_Version = match.group(2)
    else:
        current_app.logger.error( "Could not parse version in the recieved version line: {}".format( Version_Line ) )
        return False, ""

    return True, NUT_Version

#=======================================================================
# Query_NUT_UPSs
#=======================================================================
def Query_NUT_UPSs( Socket_File, UPSs, Debug_Lines ):
    Request = b"LIST UPS"
    Debug_Lines.append(Request.decode())
    current_app.logger.debugv( "Command: {}".format(Request) ) 
    Socket_File.write(Request + b"\n")

    if not Parse_Server_Response( Socket_File, Request, UPSs, Debug_Lines ):
        current_app.logger.warning( "Problem encountered listing UPSs" )
        return False

    return True

#=======================================================================
# Query_NUT_Variables
#=======================================================================
def Query_NUT_Variables( Socket_File, UPSs, Debug_Lines ):
    for ups in UPSs:
        current_app.logger.debugv( "Listing variables for UPS {}".format(ups["name"]) )

        Request = b"LIST VAR " + ups["name"].encode()
        Debug_Lines.append( Request.decode() )
        current_app.logger.debugv( "Command: {}".format(Request) ) 
        Socket_File.write(Request + b"\n")

        if not Parse_Server_Response( Socket_File, Request, UPSs, Debug_Lines ):
            current_app.logger.warning( "Problem encountered listing variables of UPS: {}".format(ups["name"]) )
            return False
    return True

#=======================================================================
# Query_NUT_UPS_Clients
#=======================================================================
def Query_NUT_UPS_Clients( Socket_File, UPSs, Debug_Lines ):
    for ups in UPSs:
        current_app.logger.debugv( "Listing client devices for UPS {}".format(ups["name"]) )
        Request = b"LIST CLIENT " + ups["name"].encode()
        Debug_Lines.append(Request.decode())
        current_app.logger.debugv( "Command: {}".format(Request) ) 
        Socket_File.write(Request + b"\n")

        if not Parse_Server_Response( Socket_File, Request, UPSs, Debug_Lines ):
            current_app.logger.warning( "Problem encountered listing clients of UPS: {}".format(ups["name"]) )
            return False
    return True

#=======================================================================
# Login_NUT_Server
#=======================================================================
def Login_NUT_Server( Socket_File, Credentials, Debug_Lines ):
    Login_Steps = [
        "USERNAME {}\n".format(Credentials['username']),
        "PASSWORD {}\n".format(Credentials['password']),
        "LOGIN {}\n".format(Credentials['device'])
    ]

    Error_Pattern = re.compile(r"^ERR (.+)$")

    for Step in Login_Steps:
        Request = Step.encode()
        Socket_File.write(Request)
        Debug_Lines.append(Request.decode())

        Line = Socket_File.readline().decode()
        Debug_Lines.append(Line)

        if re.search( Error_Pattern, Line ):
            current_app.logger.warning( "NUT Login {} returned: {}".format( Step[:-1], Line[:-1] ) )
            return False
    return True

#=======================================================================
# Logout_NUT_Server
#=======================================================================
def Logout_NUT_Server( Socket_File, Debug_Lines ):
    Request = b"LOGOUT\n"
    Socket_File.write(Request)
    Debug_Lines.append(Request.decode())

    Line = Socket_File.readline().decode()
    Debug_Lines.append(Line)
    return

#=======================================================================
# Connect_To_NUT_Server
#=======================================================================
def Connect_To_NUT_Server(Target_Address, Target_Port, Credentials):
    #===================================================================
    # Open a socket to the server
    #===================================================================
    Skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Skt.settimeout(2)

    try:
        Skt.connect((Target_Address, Target_Port))
    except Exception as Error:
        current_app.logger.error( 'Unable to connect to NUT server: {}'.format(Error) ) 
        return False, []

    #===================================================================
    # Make a virtual file from the socket to enable reading lines
    #===================================================================
    Socket_File = Skt.makefile("rbw", buffering=0)
    Debug_Lines = []

    #===================================================================
    # Handle login
    #===================================================================
    if Credentials:
        if not Login_NUT_Server( Socket_File, Credentials, Debug_Lines ):
            current_app.logger.error( "Login failed." )
            return False, []

    #===================================================================
    # Query_NUT_Version
    #===================================================================
    rtn, NUT_Version = Query_NUT_Version( Skt, Socket_File, Debug_Lines )
    if rtn:
        current_app.logger.debugv( "NUT Version: {}".format( NUT_Version ) ) 
    else:
        current_app.logger.error( "Scrape abandoned while reading version." )
        return False, []

    #===================================================================
    # Read the list of UPS devices being served
    #===================================================================
    UPSs = []
    if Query_NUT_UPSs( Socket_File, UPSs, Debug_Lines ):
        current_app.logger.debugv( "NUT UPS's: {}".format( UPSs ) ) 
    else:
        current_app.logger.error( "Scrape abandoned while listing UPS's." )
        return False, []
 
    for d in UPSs:
        d['server_address'] = Target_Address
        d['server_port'] = Target_Port

    #===================================================================
    # Get all the variables for all listed UPS devices
    #===================================================================
    if not Query_NUT_Variables( Socket_File, UPSs, Debug_Lines ):
        current_app.logger.error( "Scrape abandoned while listing variables." )
        Skt.close()
        current_app.logger.debugv( "Connection to server closed" ) 
        return False, []

    #===================================================================
    # Get the client machines for all listed UPS devices
    #===================================================================
    if not Query_NUT_UPS_Clients( Socket_File, UPSs, Debug_Lines ):
        current_app.logger.debug( "Scrape of client list failed." )

    #===================================================================
    # Handle logout
    #===================================================================
    if Credentials:
        Logout_NUT_Server( Socket_File, Debug_Lines )

    current_app.logger.debugv( "NUT_UPSs: {}".format( UPSs ) )
    Skt.close()
    current_app.logger.debugv( "Connection to server closed" ) 

    Scrape_Data = {}
    Scrape_Data["nutcase_version"] = current_app.config['APP_NAME'] + " " + current_app.config['APP_VERSION']  # globals.App_Version
    Scrape_Data["server_version"]  = NUT_Version
    Scrape_Data["server_address"]  = Target_Address
    Scrape_Data["server_port"]     = Target_Port
    Scrape_Data["mode"]            = "nut" # scrape.Server_Protocol.NUT
    Scrape_Data["ups_list"]        = UPSs
    Scrape_Data["debug"]           = Debug_Lines
    return True, Scrape_Data

#=======================================================================
# Scrape entry point: Scrape_NUT_Server
#=======================================================================
def Scrape_NUT_Server( Target_Address, Target_Port = 3493 ):
    current_app.logger.debugv("Scrape started of NUT server address {} port {}".format( Target_Address, Target_Port ) ) 

    Credentials = None
    for Cred in current_app.config['CREDENTIALS']:
        if Cred['server'] == Target_Address:
            Credentials = Cred
            break

    current_app.logger.debugv("Will use {} to log in to {}".format( Credentials, Target_Address ))
    Status, Scrape_Data = Connect_To_NUT_Server(Target_Address, Target_Port, Credentials)

    if Status:
        current_app.logger.debug( "Scrape successful." ) 
        rework_data.Rework_Variables( Scrape_Data )
        # globals.Save_Data( Scrape_Data, './scrap/scrape_data.pickle' )
    else:
        current_app.logger.warning( "Scrape unsuccessful." )

    return Status, Scrape_Data
