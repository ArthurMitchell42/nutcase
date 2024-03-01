from flask import current_app

import re

from app.utils import server_constants

# =======================================================================
# Utility to print the last n lines of a log file
# =======================================================================
def Tail_File(File_Name, Display_Lines=20):
    Lines = []
    First_Line = '<pre><span style="{}">'.format(server_constants.Monospace_Small_Font)
    Last_Line  = '</span"></pre>'

    try:
        File_Handle = open(File_Name, 'r')

        Log_Pattern = re.compile(r"^([0-9-]+) ([0-9:,]+) (DEBUGVV|DEBUGV|DEBUG|INFO|WARNING|ERROR|CRITICAL|FATAL) (.+)$")   # noqa: E501
        count = 0

        while True:
            count += 1
            line = File_Handle.readline()
            if not line:
                break
            line = line
            # if globals.Coloured_Log:
            if current_app.config["COLOURED_LOG"]:
                match = re.search(Log_Pattern, line)
                if match:
                    if match.group(3) == "DEBUG":
                        Level_Colour = server_constants.HTML_Colour_Green
                    elif match.group(3) == "DEBUGV":
                        Level_Colour = server_constants.HTML_Colour_Green
                    elif match.group(3) == "DEBUGVV":
                        Level_Colour = server_constants.HTML_Colour_Green
                    elif match.group(3) == "INFO":
                        Level_Colour = server_constants.HTML_Colour_LightBlue
                    elif match.group(3) == "WARNING":
                        Level_Colour = server_constants.HTML_Colour_Yellow
                    elif match.group(3) == "ERROR":
                        Level_Colour = server_constants.HTML_Colour_Red
                    elif match.group(3) == "CRITICAL":
                        Level_Colour = server_constants.HTML_Colour_DarkRed
                    elif match.group(3) == "FATAL":
                        Level_Colour = server_constants.HTML_Colour_DarkRed
                    else:
                        Level_Colour = server_constants.HTML_Colour_Blue
                    line = '{date} {time} <span style="{lstyle}">{level}</span> {msg}<br>'.format(
                            date = match.group(1),    time = match.group(2),
                            level = match.group(3),    msg= match.group(4),
                            lstyle = Level_Colour)
            Lines.append(line)
            if len(Lines) > Display_Lines and Display_Lines > 0:
                Lines.pop(0)
        Result = [First_Line] + Lines + [Last_Line]
    except Exception as Error:
        current_app.logger.warning("Could not open log file to serve it: {} {}".format(
            File_Name, Error))
        Lines.append("<p>Could not open log file: {}</p>".format(File_Name))
        return False, Lines

    return True, Result
