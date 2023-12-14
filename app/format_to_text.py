import logging

import globals
import metric_data

#=======================================================================
# Connect to the app log
#=======================================================================
log = logging.getLogger('__main__.' + __name__)

#=======================================================================
# Enumerated types & constants
#=======================================================================
Beeper_States = {'enabled': 1, 'disabled': 2, 'muted': 3}
Old_UPS_States = {'OL': 1, 'OB': 2, 'LB': 3}

#====================================================================================================
# Find_Metric_By_Name
#====================================================================================================
def Find_Metric_By_Name( Metric_Name ):
    return next((sub for sub in metric_data.Metric_Data_List if sub['metric'] == Metric_Name), None)

#====================================================================================================
# Format_Version_Metric
#====================================================================================================
def Format_Version_Metric( Metric, Version ):
    Data = {}
    Data["metric"] = Metric["metric"]
    Data["type"] = "# TYPE {metric} {style}".format( metric=Metric["metric"], style=Metric["style"] )
    Data["unit"] = "# UNIT {metric} {unit}".format( metric=Metric["metric"], unit=Metric["unit"] )
    Data["help"] = "# HELP {metric} {help}".format( metric=Metric["metric"], help=Metric["help"] )
    Data["data"] = [ "{metric}{{version=\"{version}\"}} 1".format(  metric=Metric["metric"], version=Version ) ]
    return Data

#====================================================================================================
# Format_UPS_Info_Metric
#====================================================================================================
UPS_Info_List = [
    {"label": "description2",            "variable": "device.description"       },
    {"label": "device_type",             "variable": "device.type"              },
    {"label": "location",                "variable": "device.location"          },
    {"label": "manufacturer",            "variable": "device.mfr"               },
    {"label": "manufacturing_date",      "variable": "device.mfr.date"          },
    {"label": "model",                   "variable": "device.model"             },
    {"label": "battery_type",            "variable": "battery.type"             },
    {"label": "driver",                  "variable": "driver.name"              },
    {"label": "driver_version",          "variable": "driver.version"           },
    {"label": "driver_version_internal", "variable": "driver.version.internal"  },
    {"label": "driver_version_data",     "variable": "driver.version.data"      },
    {"label": "usb_vendor_id",           "variable": "ups.vendorid"             },
    {"label": "usb_product_id",          "variable": "ups.productid"            },
    {"label": "ups_firmware",            "variable": "ups.firmware"             },
    {"label": "ups_type",                "variable": "ups.type"                 },
    {"label": "type",                    "variable": "device.type"              },
    {"label": "nut_version",             "variable": "driver.version"           }
    ]

def Get_NUT_Variable( ups, Variable_Name ):
    Variable = next((sub for sub in ups["variables"] if sub['name'] == Variable_Name), None)
    if Variable:
        Value = str( Variable["value"] )
    else:
        Value = None
    return Value

def Format_UPS_Info_Metric( Metric, ups ):
    Data = {}
    Data["metric"] = Metric["metric"]
    Data["type"] = "# TYPE {metric} {style}".format( metric=Metric["metric"], style=Metric["style"] )
    Data["unit"] = "# UNIT {metric} {unit}".format( metric=Metric["metric"], unit=Metric["unit"] )
    Data["help"] = "# HELP {metric} {help}".format( metric=Metric["metric"], help=Metric["help"] )

    Labels = ""
    for Entry in UPS_Info_List:
        Variable_Value = Get_NUT_Variable(ups, Entry["variable"])
        if Variable_Value:
            Labels += "," + Entry["label"] + "=\"" + Variable_Value + "\""

    Data["data"] = [ "{metric}{{ups=\"{name}\",description=\"{ups_desc}\"{labels}}} 1".format(  metric=Metric["metric"], name=ups["name"], ups_desc=ups["description"], labels=Labels ) ]
    return Data

#====================================================================================================
# Format_UPS_Status_Metric
#====================================================================================================
UPS_Status_List = [ "OL", "OB", "LB", "CHRG", "RB", "FSD", "BYPASS", "SD", "CP", "BOOST", "OFF" ]

def Format_UPS_Status_Metric( Metric, ups ):
    Data = {}
    Data["metric"] = Metric["metric"]
    Data["type"] = "# TYPE {metric} {style}".format( metric=Metric["metric"], style=Metric["style"] )
    Data["unit"] = "# UNIT {metric} {unit}".format( metric=Metric["metric"], unit=Metric["unit"] )
    Data["help"] = "# HELP {metric} {help} (\"{nut_var}\")".format( metric=Metric["metric"], help=Metric["help"], nut_var=Metric["nut_var"] )
    Data["data"] = []

    Status_List = Get_NUT_Variable(ups, "ups.status").split()
    for Status in UPS_Status_List:
        if Status.upper() in Status_List:
            Value = "1"
        else:
            Value = "0"
        Data["data"].append( "{metric}{{ups=\"{name}\",status=\"{status}\"}} {value}".format(  metric=Metric["metric"], name=ups["name"], status=Status, value=Value ) )

    return Data

#====================================================================================================
# Format_Var_Metric
#====================================================================================================
def Format_Variable_Metric(Metric, UPS_Name, NUT_Variable):
    if Metric["type"] == metric_data.Variable_Type.NONE:
        return None
    
    Data = {}
    Data["metric"] = Metric["metric"]
    Data["type"] = "# TYPE {metric} {style}".format( metric=Metric["metric"], style=Metric["style"] )
    Data["unit"] = "# UNIT {metric} {unit}".format( metric=Metric["metric"], unit=Metric["unit"] )
    Data["help"] = "# HELP {metric} {help} (\"{nut_var}\")".format( metric=Metric["metric"], help=Metric["help"], nut_var=Metric["nut_var"] )

    #=====================================================================================
    # Convert the string from the scrape to the output type
    # These are mostly maps from enumerated type strings to integers
    #
    if Metric["format"] ==  metric_data.Variable_Format.BEEPERSTATUS:
        if NUT_Variable["value"].lower() in Beeper_States:
            Var_Value = str( Beeper_States[NUT_Variable["value"]] )
        else:
            Var_Value = "0"
    elif Metric["format"] ==  metric_data.Variable_Format.PERCENTAGE:
        Var_Value = str( float(NUT_Variable["value"])/100 )
    elif Metric["format"] ==  metric_data.Variable_Format.OLDUPSSTATUS:
        if NUT_Variable["value"].upper() in Old_UPS_States:
            Var_Value = str( Old_UPS_States[NUT_Variable["value"]] )
        else:
            Var_Value = "0"
    else:
        Var_Value = NUT_Variable["value"]

    #=====================================================================================
    # Format the number for output
    # Make sure floats always contains a decimal point and that ints never do
    #
    if Metric["type"] == metric_data.Variable_Type.INTEGER:
        Value = format(int(Var_Value))
    elif Metric["type"] == metric_data.Variable_Type.FLOAT:
        Value = format(float(Var_Value), ".17f")
    else:
        Value = Var_Value
    
    Data["data"] = [ "{metric}{{ups=\"{ups_name}\"}} {value}".format(  metric=Metric["metric"], ups_name=UPS_Name, value=Value ) ]

    return Data

#====================================================================================================
# Get_Metric_Text
# Prints the 4 lines of text for a metric
#====================================================================================================
def Get_Metric_Text(Metric):
    Text  = Metric["type"] + "\n"
    Text += Metric["unit"] + "\n"
    Text += Metric["help"] + "\n"
    for Line in Metric["data"]:
        Text += Line + "\n"
    return Text

#====================================================================================================
# Format_For_Prometheus
# Main function to return data for Prometheus
#====================================================================================================
def Format_For_Prometheus( Scrape_Data ):
    log.debug("In Format_For_Prometheus. Scrape_Data is:\n{}".format( Scrape_Data ))

    #==============================================================================
    # Add system information to the list of metrics
    #==============================================================================
    Metric_List = []
    Metric_List.append(Format_Version_Metric( Find_Metric_By_Name("nut_exporter_info"), globals.App_Version ))
    Metric_List.append(Format_Version_Metric( Find_Metric_By_Name("nut_server_info"), Scrape_Data["server_version"] ))
    Metric_List.append(Format_Version_Metric( Find_Metric_By_Name("nut_info"), Scrape_Data["server_version"] ))

    #==============================================================================
    # Add each found variable for all the found UPS devices to the list of metrics
    #==============================================================================
    for ups in Scrape_Data["ups_list"]:
        Metric_List.append(Format_UPS_Info_Metric( Find_Metric_By_Name("nut_ups_info"), ups ))
        Metric_List.append(Format_UPS_Status_Metric( Find_Metric_By_Name("nut_ups_status"), ups ))
        for NUT_Variable in ups["variables"]:
            for Metric in metric_data.Metric_Data_List:
                if NUT_Variable["name"] == Metric["nut_var"]:
                    Entry = Format_Variable_Metric( Metric, ups["name"], NUT_Variable )
                    if Entry: Metric_List.append( Entry )

    Formatted_Text = ""
    if globals.Order_Metrics:
        #==============================================================================
        # Print the data for each metric to a list of lines in a given display order
        #==============================================================================
        for Display in metric_data.Metric_Data_List:
            for Metric in Metric_List:
                if Metric['metric'] == Display['metric']:
                    Formatted_Text += Get_Metric_Text(Metric)
    else:
        #==============================================================================
        # Print the data for each metric to a list of lines in the order recieved
        #==============================================================================
        for Metric in Metric_List:
            Formatted_Text += Get_Metric_Text(Metric)

    Formatted_Text += "# EOF\n"
    return Formatted_Text
