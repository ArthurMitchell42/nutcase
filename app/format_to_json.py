import logging
import json                      # For returning JSON structures

import globals

log = logging.getLogger('__main__.' + __name__)

#====================================================================================================
# Format_For_Prometheus
# Main function to return data for Prometheus
#====================================================================================================
def Format_To_JSON( Scrape_Data ):
    log.debug("In Format_To_JSON. Scrape_Data is:\n{}".format( Scrape_Data ))

    Output_Dict = {}
    Output_Dict["server_version"] = Scrape_Data["server_version"] 
    Output_Dict["server_address"] = Scrape_Data["server_address"] 
    Output_Dict["server_port"]    = Scrape_Data["server_port"] 

    for ups in Scrape_Data["ups_list"]:
        Output_Dict[ ups["name"] ] = {}
        Output_Dict[ ups["name"] ]["description"] = ups["description"]
        for Var in ups["variables"]:
            Output_Dict[ ups["name"] ][ Var["name"] ] = Var["value"]

    log.debug("Output_Dict: \n{}".format(Output_Dict))
    Formatted_JSON_Text = json.dumps(Output_Dict)
    return Formatted_JSON_Text
