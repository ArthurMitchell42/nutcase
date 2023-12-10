import logging
import json                      # For returning JSON structures

#=======================================================================
# Connect to the app log
#=======================================================================
log = logging.getLogger('__main__.' + __name__)

#====================================================================================================
# Format_To_JSON
# Main function to return JSON data
#====================================================================================================
def Format_To_JSON( Scrape_Data ):
    log.debug("In Format_To_JSON. Scrape_Data is:\n{}".format( Scrape_Data ))

    Output_Dict = {}
    if "server_version" in Scrape_Data:
        Output_Dict["server_version"] = Scrape_Data["server_version"] 
    if "server_address" in Scrape_Data:
        Output_Dict["server_address"] = Scrape_Data["server_address"] 
    if "server_port" in Scrape_Data:
        Output_Dict["server_port"]    = Scrape_Data["server_port"] 

    if "ups_list" in Scrape_Data:
        for ups in Scrape_Data["ups_list"]:
            Output_Dict[ ups["name"] ] = {}
            Output_Dict[ ups["name"] ]["description"] = ups["description"]
            for Var in ups["variables"]:
                Output_Dict[ ups["name"] ][ Var["name"] ] = Var["value"]
            if "clients" in ups:
                Output_Dict[ ups["name"] ]["clients" ] = {}
                Output_Dict[ ups["name"] ]["clients" ]["count"] = len(ups["clients"])
                Output_Dict[ ups["name"] ]["clients" ]["list"] = ups["clients"]

    log.debug("Output_Dict: \n{}".format(Output_Dict))
    Formatted_JSON_Text = json.dumps(Output_Dict)
    return Formatted_JSON_Text
