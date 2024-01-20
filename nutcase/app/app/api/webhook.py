import json                                     # For webhooks
from urllib.request import urlopen              # For webhooks
from urllib.error   import URLError, HTTPError  # For webhooks
from urllib.parse import parse_qs, urlsplit, urlunsplit, urlencode
from http import HTTPStatus

#====================================================================================================
# Call a named WebHook
#====================================================================================================
def Call_URL( app, URL ):
    try:
        Response = urlopen( URL )
        HTTP_Code = Response.getcode()
        if HTTP_Code != HTTPStatus.OK:
            app.logger.warning("WebHook {} returned {}: {}".format( 
                                            URL, HTTP_Code, HTTPStatus(HTTP_Code).name ) )
        Page_JSON = json.loads( Response.read() )

        if "ok" in Page_JSON:
            if Page_JSON["ok"] != True:
                if "msg" in Page_JSON:
                    Message = Page_JSON["msg"]
                else:
                    Message = "none"
                app.logger.warning("The webhook returned an 'ok' element as not True with the message '{}'".format(Message))
    except HTTPError as Error:
        if hasattr(Error, 'reason'):
            app.logger.warning("Failed to call webhook. Reason: {}".format(Error.reason) )
        if hasattr(Error, 'code'):
            app.logger.warning("The webhook server could not fulfill the request. Error code: {}".format(Error.code))
        return
    except URLError as Error:
        if hasattr(Error, 'reason'):
            app.logger.warning("Failed to call webhook. Reason: {}".format(Error.reason) )
        return
    return

#====================================================================================================
# Modify a WebHook if it has suitable fields
#   If a query string is present in the refactoring it is either used to modify the field in the 
#   webhook or is added to the URL.
#====================================================================================================
def Refactor_URL_Query( Hook, Refactor ):
    Parsed_URL_tup = urlsplit(Hook)                                  # Split the URL into components
    Query = parse_qs( Parsed_URL_tup.query, keep_blank_values=True ) # Split the query value pairs
    for r in Refactor:                                               # Change/add queries to the URL
        Query[ r ] = [ Refactor[r] ]                                 # from the Refactor dictionary

    Parsed_URL     = list( Parsed_URL_tup )                          # Make the components mutable
    Parsed_URL[3]  = urlencode(Query, doseq=True)                    # Put the query back together
    Refactored_URL = urlunsplit(Parsed_URL)                          # Put the URL back together
    return Refactored_URL

#====================================================================================================
# Call a named WebHook
#   If the name is not present then look for the 'default' hook
#   If niether are present then just log a warning and return
#   Either call a single webhook or call a list of hooks sequentially
#====================================================================================================
def Call_Webhook( app, Name, Refactor = {} ):
    if len(app.config["WEBHOOKS"]) > 0:
        if Name not in app.config["WEBHOOKS"]:
            if 'default' in app.config["WEBHOOKS"]:
                Name = 'default'
            else:
                app.logger.warning("WebHook name missing {} and no default is set.".format( Name ))
                return

        app.logger.debug("Calling WebHook {}".format( Name ))
        if isinstance( app.config["WEBHOOKS"][Name], str):
            Call_URL( app, Refactor_URL_Query( app.config["WEBHOOKS"][Name], Refactor ) )
        elif isinstance( app.config["WEBHOOKS"][Name], list):
            for Hook in app.config["WEBHOOKS"][Name]:
                Call_URL( app, Refactor_URL_Query( Hook, Refactor ) )

    return
