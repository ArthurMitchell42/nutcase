from flask import current_app

# ==================================================================================================
# Filter_JSON
# ==================================================================================================
def Filter_JSON(Input_Dict, JSON_Elements):
    Output_Dict = {}
    if not JSON_Elements or not Input_Dict:
        return Output_Dict

    for Element in JSON_Elements:
        Temp_Data = Input_Dict
        Path = Element.split("/")

        for Index in range(0, len(Path)):
            Key = Path[Index]
            if Key in Temp_Data:
                if isinstance(Temp_Data[Key], dict):
                    Temp_Data = Temp_Data[Key]
                    continue
                elif isinstance(Temp_Data[Key], list):
                    try:
                        List_Index = int(Path[Index + 1])
                        Output_Dict[Element] = Temp_Data[Key][List_Index]
                    except Exception as Error:
                        Output_Dict[Element] = "Index {} not found {}".format(Element, Error)
                    finally:
                        break
                else:
                    Output_Dict[Element] = Temp_Data[Key]
                    break
            else:
                Output_Dict[Element] = "Key {} not found".format(Element)
                break

    return Output_Dict

# ==================================================================================================
# Format_For_JSON
# Main function to return a dictionary suitable for turning in to JSON data
# ==================================================================================================
def Format_For_JSON(Scrape_Data, JSON_Elements):
    current_app.logger.debug("Scrape_Data is:\n{} Requested element is {}".format(
        Scrape_Data, JSON_Elements))

    Output_Dict = {}
    if not Scrape_Data:
        return Output_Dict

    if "nutcase_version" in Scrape_Data:
        Output_Dict["nutcase_version"] = Scrape_Data["nutcase_version"]
    if "server_version" in Scrape_Data:
        Output_Dict["server_version"] = Scrape_Data["server_version"]
    if "server_address" in Scrape_Data:
        Output_Dict["server_address"] = Scrape_Data["server_address"]
    if "server_port" in Scrape_Data:
        Output_Dict["server_port"] = Scrape_Data["server_port"]
    if "logs" in Scrape_Data:
        Output_Dict["logs"] = Scrape_Data["logs"]

    if "ups_list" in Scrape_Data:
        for ups in Scrape_Data["ups_list"]:
            Output_Dict[ups["name"]] = {}
            Output_Dict[ups["name"]]["description"] = ups["description"]
            for Var in ups["variables"]:
                Output_Dict[ups["name"]][Var["name"]] = Var["value"]
            if "clients" in ups:
                Output_Dict[ups["name"]]["clients"] = {}
                Output_Dict[ups["name"]]["clients"]["count"] = len(ups["clients"])
                Output_Dict[ups["name"]]["clients"]["list"] = ups["clients"]
            if "logs" in ups:
                Output_Dict[ups["name"]]["logs"] = ups["logs"]

    if JSON_Elements:
        Output_Dict = Filter_JSON(Output_Dict, JSON_Elements)

    # globals.Save_Data( Output_Dict, "./scrap/output_dict.pickle" )

    current_app.logger.debug("Output_Dict:\n{}".format(Output_Dict))
    return Output_Dict
