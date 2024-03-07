import json
import urllib
from urllib.error import URLError, HTTPError
from http import HTTPStatus

from flask import current_app

HTML_Update = '''<a href="{url}" target="_blank" class="text-decoration-none text-small badge rounded-pill {style}">{text}</a>'''
HTML_Note = 'bg-success text-light'
HTML_Warn = 'bg-warning text-dark'
HTML_Alert = 'bg-danger text-light'

# ==================================================================================================
# Call a named WebHook
# ==================================================================================================
def Get_Update_String():
    Result = ""
    try:
        URL = current_app.config['GITHUB_API_URL'] + "releases"
        Response = urllib.request.urlopen(URL)
        HTTP_Code = Response.getcode()
        if HTTP_Code != HTTPStatus.OK:
            current_app.logger.warning("Github returned {}: {}".format(
                                    HTTP_Code, HTTPStatus(HTTP_Code).name))
            return Result
        try:
            Page_JSON = json.loads(Response.read())
            current_app.logger.debugv("JSON Returned by Github {}".format( json.dumps(Page_JSON, indent=4)))

            if len(Page_JSON) > 0:
                Current_Version = "v" + current_app.config['APP_VERSION']
                for rel in Page_JSON:
                    Tag = rel['tag_name'].lower()
                    if Tag == Current_Version or \
                            Tag.startswith(Current_Version + "_"):
                        break
                    elif rel['draft'] is True:
                        continue
                    elif rel['prerelease'] is False:
                        Link = rel['html_url']
                        Ver_Text = rel['tag_name']
                        if "security" in rel['body'].lower() or "urgent" in rel['body'].lower():
                            Style_Text = HTML_Alert
                        else:
                            Style_Text = HTML_Warn
                        Result = HTML_Update.format(url=Link, style=Style_Text, text=Ver_Text)
                        break
                    elif rel['prerelease'] is True:
                        Link = rel['html_url']
                        Ver_Text = rel['tag_name']
                        Body = rel['body'].lower()
                        if "security" in Body or "urgent" in Body:
                            Style_Text = HTML_Alert
                        else:
                            Style_Text = HTML_Note
                        Result = HTML_Update.format(url=Link, style=Style_Text, text=Ver_Text)
                        continue
        except json.decoder.JSONDecodeError as Error:
            current_app.logger.warning("JSON Returned by Github could not be parsed {}".format(Error))
    except HTTPError as Error:
        if hasattr(Error, 'reason'):
            current_app.logger.warning("Failed to call Github API. Reason: {}".format(Error.reason))
        if hasattr(Error, 'code'):
            current_app.logger.warning("Github couldn't fulfill request Error: {}".format(
                Error.code))
    except URLError as Error:
        if hasattr(Error, 'reason'):
            current_app.logger.warning("Failed to call Github API. Reason: {}".format(Error.reason))
    return Result
