import json
import urllib
from urllib.error import URLError, HTTPError
from urllib.parse import parse_qs, urlsplit, urlunsplit, urlencode
from http import HTTPStatus

# ==================================================================================================
# Call a named WebHook
# ==================================================================================================
def Call_URL(app, URL):
    try:
        Response = urllib.request.urlopen(URL)
        HTTP_Code = Response.getcode()
        if HTTP_Code != HTTPStatus.OK:
            app.logger.warning("WebHook returned {}: {}".format(
                                    HTTP_Code, HTTPStatus(HTTP_Code).name))
        try:
            Page_JSON = json.loads(Response.read())
            app.logger.debugvv("JSON Returned by a web hook {}".format(Page_JSON))
            if "ok" in Page_JSON:
                if Page_JSON["ok"] is not True:
                    if "msg" in Page_JSON:
                        Message = Page_JSON["msg"]
                    else:
                        Message = "none"
                    app.logger.warning(
                        "The webhook returned an 'ok' element "
                        "as not True with the message '{}'".format(
                            Message))
        except json.decoder.JSONDecodeError as Error:
            app.logger.warning("JSON Returned by a web hook could not be parsed {}".format(Error))
    except HTTPError as Error:
        if hasattr(Error, 'reason'):
            app.logger.warning("Failed to call webhook. Reason: {}".format(Error.reason))
        if hasattr(Error, 'code'):
            app.logger.warning("Webhook server couldn't fulfill request Error: {}".format(
                Error.code))
        return False
    except URLError as Error:
        if hasattr(Error, 'reason'):
            app.logger.warning("Failed to call webhook. Reason: {}".format(Error.reason))
        return False
    return True

# ==================================================================================================
# Modify a WebHook if it has suitable fields
#   If a query string is present in the refactoring it is either used to modify the field in the
#   webhook or is added to the URL.
# ==================================================================================================
def Refactor_URL_Query(Hook, Refactor):
    Parsed_URL_tup = urlsplit(Hook)                                 # Split the URL into components
    Query = parse_qs(Parsed_URL_tup.query, keep_blank_values=True)  # Split the query value pairs
    Query.update(Refactor)            # Change/add queries to the URL from the Refactor dictionary
    Parsed_URL     = list(Parsed_URL_tup)                         # Make the components mutable
    Parsed_URL[3]  = urlencode(Query, doseq=True)                 # Put the query back together
    Refactored_URL = urlunsplit(Parsed_URL)                       # Put the URL back together
    return Refactored_URL

# ==================================================================================================
# Call a named WebHook
#   If the name is not present then look for the 'default' hook
#   If niether are present then just log a warning and return
#   Either call a single webhook or call a list of hooks sequentially
# ==================================================================================================
def Call_Webhook(app, Name, Refactor = {}):
    if len(app.config["WEBHOOKS"]) == 0:
        return False
    if Name not in app.config["WEBHOOKS"]:
        if 'default' in app.config["WEBHOOKS"]:
            Name = 'default'
        else:
            app.logger.warning("WebHook name missing {} and no default is set.".format(Name))
            return False

    app.logger.debugvv("Calling WebHook {}".format(Name))
    if isinstance(app.config["WEBHOOKS"][Name], str):
        Call_URL(app, Refactor_URL_Query(app.config["WEBHOOKS"][Name], Refactor))
    elif isinstance(app.config["WEBHOOKS"][Name], list):
        for Hook in app.config["WEBHOOKS"][Name]:
            Call_URL(app, Refactor_URL_Query(Hook, Refactor))

    return True
