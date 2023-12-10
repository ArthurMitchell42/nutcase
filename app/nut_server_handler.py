import logging
import re
import socket
# import pickle                    # For debug only, saves data dictionary to disk

from enum import Enum

import rework_data
import globals

#=======================================================================
# Connect to the app log
#=======================================================================
log = logging.getLogger('__main__.' + __name__)

#=======================================================================
# Enumerated types
#=======================================================================
NUT_Query_List_State = Enum('NUT_Query_List_State', ['INITIAL', 'STARTED', 'ENDED', 'MALFORMED', 'ERROR'])

#=======================================================================
# Query_NUT_Version
#=======================================================================
def Query_NUT_Version( Socket, Socket_File, Debug_Lines ):
    Error_Pattern = re.compile("^ERR (.+)$")
    Version_Pattern = re.compile("^(.+) upsd (.+) - (.+)$")

    Request = b"VER\n"
    Socket_File.write(Request)
    Debug_Lines.append(Request.decode())

    data = Socket_File.readline()
    Version_Line = data.decode()
    Debug_Lines.append(Version_Line)

    if Version_Line[-1] == "\n":
        Version_Line = Version_Line[:-1]

    log.debug( "NUT Version line: {}".format( Version_Line ) ) 

    match = re.search(Error_Pattern, Version_Line)
    if match:
        log.error( "The NUT server returned an error when asked for its version: {}".format( Version_Line ) )
        if match.group(1) == "ACCESS-DENIED":
            IPAddr = Socket.getsockname()[0]
            log.error( "ACCESS-DENIED may mean the NUT server has not had my IP address ({}) added to its allowed list.".format( IPAddr ) )
        return False, ""

    match = re.search(Version_Pattern, Version_Line)
    if match:
        NUT_Version = match.group(2)
    else:
        log.error( "Could not parse version in the recieved version line: {}".format( Version_Line ) )
        return False, ""

    return True, NUT_Version

#=======================================================================
# Query_NUT_UPS_Clients
#=======================================================================
def Query_NUT_UPS_Clients( Socket_File, UPSs, Debug_Lines ):
    for ups in UPSs:
        log.debug( "Listing client devices for UPS {}".format(ups["name"]) )
        Request = b"LIST CLIENT " + ups["name"].encode()

        log.debug( "Command: {}".format(Request) ) 
        Socket_File.write(Request + b"\n")

        rtn = Parse_Server_Response( Socket_File, Request, UPSs, Debug_Lines )

        if not rtn:
            log.warning( "Problem encountered listing variables of UPS: {}".format(ups["name"]) )
            return False

    return True

#=======================================================================
# Read server respose
#=======================================================================
def Parse_Server_Response( Socket_File, Request, UPSs, Debug_Lines ):

    Begin_Pattern       = re.compile("^BEGIN " + Request.decode() + "$")
    End_Pattern         = re.compile("^END " + Request.decode() + "$")
    Error_Pattern       = re.compile("^ERR (.+)$")
    UPS_Pattern         = re.compile('^UPS (.+?) (.*)$')
    VAR_Pattern         = re.compile('^VAR (.+?) (.+?) (.*)$')
    UPS_Client_Pattern  = re.compile('^CLIENT (.+?) (.*)$')

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
                            # log.debug( "UPS match" )
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
                            # log.debug( "VAR match {} for UPS {}".format( VAR, var_match.group(1) ) )

                            for i in UPSs:
                                # log.debug( "Found UPS {}".format( i ) )
                                if i["name"] == var_match.group(1):
                                    # log.debug( "Found UPS {} for VAR {}".format( var_match.group(1), var_match.group(2) ) )
                                    i["variables"].append(VAR)
                        elif client_match:
                            Client = {
                                "upsname": client_match.group(1),
                                "client": client_match.group(2)
                            }
                            log.debug( "Client match {} for UPS {}".format( Client["client"], Client["upsname"] ) )

                            for i in UPSs:
                                # log.debug( "Found UPS {}".format( i ) )
                                if i["name"] == client_match.group(1):
                                    # log.debug( "Found UPS {} for VAR {}".format( var_match.group(1), var_match.group(2) ) )
                                    i["clients"].append(Client["client"])
                        else:
                            List_State = NUT_Query_List_State.MALFORMED
                            break
    except Exception as Error:
        log.error( "Error scraping server: {}".format(Error) )
        return False
    
    if List_State == NUT_Query_List_State.MALFORMED:
        log.error( "Malformed response from server: {}".format(Line) ) 
        return False
    if List_State == NUT_Query_List_State.ERROR:
        log.error( "Error from server: {}".format(Line) ) 
        return False
    
    log.debug( "List_State {}".format( List_State ) ) 

    return True

#=======================================================================
# Query_NUT_UPSs
#=======================================================================
def Query_NUT_UPSs( Socket_File, UPSs, Debug_Lines ):
    Request = b"LIST UPS"
    Debug_Lines.append(Request.decode())
    log.debug( "Command: {}".format(Request) ) 
    Socket_File.write(Request + b"\n")

    rtn = Parse_Server_Response( Socket_File, Request, UPSs, Debug_Lines )
    if not rtn:
        log.warning( "Problem encountered listing variables of UPS" )
        return False

    return True

#=======================================================================
# Query_NUT_Variables
#=======================================================================
def Query_NUT_Variables( Socket_File, UPSs, Debug_Lines ):
    for ups in UPSs:
        # Debug_Lines = []
        log.debug( "Listing variables for UPS {}".format(ups["name"]) )

        Request = b"LIST VAR " + ups["name"].encode()
        Debug_Lines.append( Request.decode() )
        log.debug( "Command: {}".format(Request) ) 
        Socket_File.write(Request + b"\n")

        rtn = Parse_Server_Response( Socket_File, Request, UPSs, Debug_Lines )
        # ups["debug"] = Debug_Lines
        if not rtn:
            log.warning( "Problem encountered listing variables of UPS: {}".format(ups["name"]) )
            return False
         
    return True

#=======================================================================
# Connect_To_NUT_Server
#=======================================================================
def Connect_To_NUT_Server(Target_Address, Target_Port):
    #===================================================================
    # Open a socket to the server
    #===================================================================
    Skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Skt.settimeout(2)

    try:
        Skt.connect((Target_Address, Target_Port))
    except Exception as Error:
        log.error( 'Unable to connect to NUT server: {}'.format(Error) ) 
        return False, []

    #===================================================================
    # Make a virtual file from the socket to enable reading lines
    #===================================================================
    File_Handle = Skt.makefile("rbw", buffering=0)

    Server_Debug_Lines = []
    rtn, NUT_Version = Query_NUT_Version( Skt, File_Handle, Server_Debug_Lines )
    if rtn:
        log.debug( "NUT Version: {}".format( NUT_Version ) ) 
    else:
        log.error( "Scrape abandoned while reading version." )
        return False, []

    #===================================================================
    # Read the list of UPS devices being served
    #===================================================================
    UPSs = []
    rtn = Query_NUT_UPSs( File_Handle, UPSs, Server_Debug_Lines )
    if rtn:
        log.debug( "NUT UPS's: {}".format( UPSs ) ) 
    else:
        log.error( "Scrape abandoned while listing UPS's." )
        return False, []
 
    #===================================================================
    # Get all the variables for all listed UPS devices
    #===================================================================
    rtn = Query_NUT_Variables( File_Handle, UPSs, Server_Debug_Lines )
    if not rtn:
        log.error( "Scrape abandoned while listing variables." )
        Skt.close()
        log.debug( "Connection to server closed" ) 
        return False, []

    #===================================================================
    # Get the client machines for all listed UPS devices
    #===================================================================
    rtn = Query_NUT_UPS_Clients( File_Handle, UPSs, Server_Debug_Lines )
    if not rtn:
        log.debug( "Scrape of client list failed." )

    log.debug( "NUT_UPSs: {}".format( UPSs ) )
    Skt.close()
    log.debug( "Connection to server closed" ) 

    Scrape_Data = {}
    Scrape_Data["server_version"] = NUT_Version
    Scrape_Data["server_address"] = Target_Address
    Scrape_Data["server_port"]    = Target_Port
    Scrape_Data["ups_list"]       = UPSs
    Scrape_Data["debug"]          = Server_Debug_Lines

    return True, Scrape_Data

#=======================================================================
# Scrape entry point: Scrape_NUT_Server
#=======================================================================
def Scrape_NUT_Server( Target_Address, Target_Port = 3493 ):
    log.debug("Scrape started of NUT server, address %s, port %s" % (Target_Address, Target_Port) ) 
    log.debug("Scrape_NUT_Server: Config in use: {}".format( globals.Config ))

    Status, Scrape_Data = Connect_To_NUT_Server(Target_Address, Target_Port)
    if Status:
        log.debug( "Scrape successful." ) 
        if globals.Config:
            log.debug( "Reworking variables." ) 
            rework_data.Rework_Variables( Scrape_Data, globals.Config )
        else:
            log.debug( "Not reworking variables." ) 

        # with open('./scrap/scrape_data.pickle', 'wb') as handle:
        #     pickle.dump(Scrape_Data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    else:
        log.warning( "Scrape unsuccessful." )

    return Status, Scrape_Data
