#====================================================================================================
# HTML Font & style strings
#====================================================================================================
Main_Font             = 'font-family: Arial, Helvetica, sans-serif;'
Lucida_Font           = 'font-family:Lucida Sans Unicode;'
Verdana_Font          = 'font-family:Verdana;'
Lucida_Console_Font   = 'font-family:Lucida Console;'
Monospace_Font        = 'font-family:monospace;font-size:14px;'
Monospace_Small_Font  = 'font-family:monospace;font-size:12px;'

HTML_Colour_Blue      = 'color:Blue;'
HTML_Colour_Yellow    = 'color:Gold;'
HTML_Colour_Green     = 'color:LimeGreen;'
HTML_Colour_DarkGreen = 'color:Green;'
HTML_Colour_Red       = 'color:OrangeRed;'
HTML_Colour_DarkRed   = 'color:Crimson;'
HTML_Colour_LightBlue = 'color:DarkTurquoise;'

#====================================================================================================
# HTML Constants
#====================================================================================================
Accepts_Openmetrics = 'application/openmetrics-text'

Content_Types = {
    'text':         'text/plain; charset=UTF-8',
    'html':         'text/html; charset=UTF-8',
    'json':         'application/json; charset=UTF-8',
    'openmetrics':  'application/openmetrics-text; version=1.0.0; charset=UTF-8',
}

#====================================================================================================
# HTML Response lines
#====================================================================================================
Title_Colour = HTML_Colour_DarkGreen
Line_Colour  = HTML_Colour_Blue

HTML_Usage = [
    '<p style="{}">Usage examples:</p><pre>'.format( Main_Font ),

    '<span style="{}{}"><b>Valid end-points (paths).</b></span><br>'.format( Main_Font, Title_Colour ),
    '<span style="{}{}">'.format( Monospace_Font, Line_Colour ),
    '<b>/help</b>         Returns this message.<br>',
    '<b>/log</b>          Displays the last log lines<br>',
    '<b>/health</b>       Returns a JSON structure to confirm NUTCase is alive.<br>',
    '<b>/metrics</b>      Returns text output compatible with Prometheus scraping.<br>',
    '<b>/json</b>         Returns JSON output compatible with HomePage and Webhooks.<br>',
    '<b>/raw</b>          Returns JSON output suitable only for diagnostics.<br>',
    '<b>/apclog</b>       Displays the event log of an APC server.<br>',
    '<br></span>',

    '<span style="{}{}"><b>Valid parameters.</b></span><br>'.format( Main_Font, Title_Colour ),
    '<span style="{}{}">'.format( Monospace_Font, Line_Colour ),
    '<b>lines</b>         Sets the number of lines to display. Only valid with /log<br>',
    '<b>mode</b>          Optional. Specifies apc or nut mode. Default is nut.<br>',
    '<b>target</b>        Specifies address and, optionally, port of the server.<br>',
    '<b>addr</b>          Specifies address of the server as an alternative to target.<br>',
    '<b>port</b>          Overrides the server default port if usering addr<br>',
    '<br></span>',

    '<span style="{}{}"><b>Specifying the server parameters.</b></span><br>'.format( Main_Font, Title_Colour ),
    '<span style="{}{}">   Note: this is valid for end-points json, raw & metrics</span><br>'.format( Main_Font, Title_Colour ),
    '<span style="{}{}">'.format( Monospace_Font, Line_Colour ),
    '<b>/metrics?target=A.B.C.D</b>       Specify the address of the server, assuming the default port.<br>',
    '<b>/metrics?target=A.B.C.D:P</b>     Specify the address of the server and the port (p).<br>',
    '<b>/metrics?addr=A.B.C.D</b>         Specify the address of the server, assuming the default port.<br>',
    '<b>/metrics?addr=A.B.C.D&port=P</b>  Specify the address of the server and the port (P).<br>',
    '<br></span>',

    '<span style="{}{}"><b>Specifying an APC server parameters.</b></span><br>'.format( Main_Font, Title_Colour ),
    '<span style="{}{}">   Note: this is valid for end-points json & raw. All other combinations of target, addr & port (above) are valid</span><br>'.format( Main_Font, Title_Colour ),
    '<span style="{}{}">         All other combinations of target, addr & port (above) are valid</span><br>'.format( Main_Font, Title_Colour ),
    '<span style="{}{}">         mode=nut is also valid for NUT servers but is the default and need not be given.</span><br>'.format( Main_Font, Title_Colour ),
    '<span style="{}{}">'.format( Monospace_Font, Line_Colour ),
    '<b>/json?mode=apc&target=A.B.C.D</b>       Specify the address of the server, assuming the default port.<br>',
    '<br></span>',

    '<span style="{}{}"><b>View the log file.</b></span><br>'.format( Main_Font, Title_Colour ),
    '<span style="{}{}">'.format( Monospace_Font, Line_Colour ),
    '<b>/log</b>                          View the the last default (20) number of lines from the log.<br>',
    '<b>/log?lines=30</b>                 View the the last Specifyed number of lines from the log.<br>',
    '<br></span>',

    '<span style="{}{}"><b>For example, if your NUT server is at 10.0.20.50, serving on the default port (3493) and nutcase is on address 10.0.20.40 on the default port (9995) then to get data for Prometheus enter:</b></span><br>'.format( Main_Font, Title_Colour ),
    '<span style="{}{}">'.format( Monospace_Font, Line_Colour ),
    '<span style="margin-left: 20px;"><b>http://10.0.20.40:9995/metrics?target=10.0.20.50:3493</b></span>',
    '<br></span>',

    '</pre><p style="{}">For details go to <a href="https://github.com/ArthurMitchell42/nutcase">NUTCase on GitHub</a></p>'.format( Main_Font ),
]
