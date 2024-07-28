from flask import current_app, session
import re           # To break status words
import time         # To format time variables
import arrow        # To print human readable times
import os

from app.utils import format_to_text
from app.utils import configuration
from app.utils import apc_to_nut

# =============================================================================
# region Constatnts for GUI
# =============================================================================
Icon_Line            = 'bi-plugin'
Icon_Bat_Charging    = 'bi-battery-charging'
Icon_Bat_Full        = 'bi-battery-full'
Icon_Bat_Half        = 'bi-battery-half'
Icon_Bat_Empty       = 'bi-battery'
Icon_Alert_Triangle  = 'bi-exclamation-triangle'
Icon_Error_Octagon   = 'bi-exclamation-octagon-fill'
Icon_Vin_Boost       = 'bi-chevron-bar-up'
Icon_Vin_Trim        = 'bi-chevron-bar-down'
Icon_Vin_Normal      = 'bi bi-distribute-vertical'
Icon_Check           = 'bi-check-circle'
Icon_Unknown         = 'bi-question-circle'

Nominal_Width = 75

# =============================================================================
# Prototype HTML blocks for GUI
# =============================================================================
Status_HTML = \
'''
<div class="d-flex">
<div class="d-flex flex-fill align-items-center justify-content-end fs-4 main-data">
{status_text}
</div>
<div class="d-flex px-3 align-items-center">
<i class="bi {line_icon} fs-3 {line_icon_style}" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-html="true" data-bs-title="{line_icon_tip}"></i>
</div>
<div class="d-flex px-3 align-items-center">
<span class="fs-4"><i class="bi {line_alert_icon} {line_alert_icon_style}" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-html="true" data-bs-title="{line_alert_tip}"></i></span>
</div>
</div>
<div class="d-flex">
<div class="d-flex flex-fill align-items-center justify-content-end main-data">
{secondary_text}
</div>
<div class="d-flex px-3 align-items-center">
<i class="bi {battery_icon} fs-3 {bat_icon_style}" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-html="true" data-bs-title="{bat_icon_tip}"></i>
</div>
<div class="d-flex px-3 align-items-center">
<span class="fs-4"><i class="bi {bat_alert_icon} {bat_alert_style}" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-html="true" data-bs-title="{bat_alert_tip}"></i></span>
</div>
</div>
'''

Runtime_HTML = \
'''
<div class="d-flex fs-4 justify-content-center {fmt}">
{time}
</div>
'''

Sounder_HTML = \
'''
<div class="d-flex fs-2 flex-fill justify-content-around">
    <div><i class="bi bi-volume-up-fill main-icon {s_enabled}"></i></div> <!-- style="--bs-text-opacity: .25;"-->
    <div><i class="bi bi-volume-off-fill main-icon {s_muted}"></i></div>
    <div><i class="bi bi-volume-mute-fill main-icon {s_disabled}"></i></div>
</div>
<div class="d-flex flex-fill justify-content-center align-items-center main-data">
    {state}
</div>
'''

Device_Pulldown_HTML = \
'''
<a class="dropdown-item {active}" href="/?addr={addr}&dev={dev}{mode_q}">
    <div class="d-flex align-items-center justify-content-between">
    <div>{addr_name} {dev_name} {mode}</div>
    <div>&nbsp<i class="bi bi-check-circle {def_style}"></i></div>
    </div>
</a>
'''

Download_Pulldown_HTML = \
'''
<a class="dropdown-item" href="/{path}?addr={addr}&download={dl_opt}&dev={dev}{mode_q}" target="_blank">
{fmt}
</a>
'''

Log_File_Pulldown_HTML = \
'''<li>
<a class="dropdown-item" href="/log/{file}">
    <div class="d-flex align-items-center justify-content-between">
    <div>{file}</div>
    <div>&nbsp&nbsp&nbsp</div>
    <div class="text-muted">{note}</div>
    </div>
</a>
</li>'''

# =============================================================================
# region Utils
# Clean_List - Utility to clean 'null' values from data so that the max
#   and min functions work
# =============================================================================
def Clean_List(Data):
    Clean = [x for x in Data if not isinstance(x, str)]
    return Clean

# =============================================================================
# Time_Axis_Array - Make the horizontal time scale axis with labels
# =============================================================================
def Time_Axis_Array(Length):
    X_Data = []
    for x in range(0, Length):
        if x == 0:
            X_Data.append('Now')
        elif x % 10 == 0:
            X_Data.append('-' + str(int(x / 2)) + "m")
        else:
            X_Data.append('')

    return list(reversed(X_Data))

# ==========================================================
# region Dougnuts
# Dougnut_Input_Voltage
# ==========================================================
def Dougnut_Input_Voltage(UPS, Result):
    if Input_Volts := format_to_text.Get_NUT_Variable(UPS, 'input.voltage'):
        Input_Volts = float(Input_Volts)
    else:
        Input_Volts = 0

    Result['input_volts'] = [0, 1]
    Result['input_nom'] = [0, 0, 1]
    Result['input_scale'] = [1, 0, 0, 0, 0]

# ==========================================================
# Decide on the max input voltage
    Input_TH = format_to_text.Get_NUT_Variable(UPS, 'input.transfer.high')
    Line_Nominal = None
    if Input_Nominal := format_to_text.Get_NUT_Variable(UPS, 'input.voltage.nominal'):
        Line_Nominal = float(Input_Nominal)
    elif Output_Nominal := format_to_text.Get_NUT_Variable(UPS, 'output.voltage.nominal'):
        Line_Nominal = float(Output_Nominal)

    Max_Input_Volts = 1
    if Input_TH:
        Input_TH = float(Input_TH)
        Max_Input_Volts = Input_TH * 1.1
    elif Line_Nominal:
        Max_Input_Volts = float(Line_Nominal) * 1.22

    if Max_Input_Volts == 0:
        Max_Input_Volts = 1
    if Input_Volts > Max_Input_Volts:
        Input_Volts = Max_Input_Volts
    Result['input_volts'] = [Input_Volts, Max_Input_Volts - Input_Volts]

# ==========================================================
# Input Voltage scale
    Input_TL = format_to_text.Get_NUT_Variable(UPS, 'input.transfer.low')
    if Input_TH and Input_TL:
        Input_TL = float(Input_TL)
        Result['input_scale'] = [0, 0, Input_TL, Input_TH - Input_TL, Max_Input_Volts - Input_TH]
    else:
        Result['input_scale'] = [1, 0, 0, 0, 0]

    if Line_Nominal:
        Result['input_nom'] = [float(Line_Nominal) - (Max_Input_Volts / (Nominal_Width * 2)),
               (Max_Input_Volts / Nominal_Width),
                Max_Input_Volts - float(Line_Nominal) - (Max_Input_Volts / (Nominal_Width * 2))]
    else:
        Result['input_nom'] = [0, 0, 1]
    return

# ==========================================================
# Dougnut graphics - Dougnut_Battery_Charge
# ==========================================================
def Dougnut_Battery_Charge(UPS, Result):
    Result['bat_charge'] = [0, 0]
    Result['bat_ch_scale'] = [1, 0, 0, 0, 0]

    if Bat_Charge_Low := format_to_text.Get_NUT_Variable(UPS, 'battery.charge.low'):
        Bat_Charge_Low = int(Bat_Charge_Low)

    if Bat_Charge_Warn := format_to_text.Get_NUT_Variable(UPS, 'battery.charge.warning'):
        Bat_Charge_Warn = int(Bat_Charge_Warn)

    if Bat_Charge_Low and Bat_Charge_Warn:
        Result['bat_ch_scale'] = [0, 0, int(Bat_Charge_Low),
                                  int(Bat_Charge_Warn) - int(Bat_Charge_Low),
                                  100 - int(Bat_Charge_Warn)]
    elif Bat_Charge_Low and not Bat_Charge_Warn:
        Result['bat_ch_scale'] = [0, 0, int(Bat_Charge_Low), 0, 100 - int(Bat_Charge_Low)]
    elif not Bat_Charge_Low and Bat_Charge_Warn:
        Result['bat_ch_scale'] = [0, 0, int(Bat_Charge_Warn), 0, 100 - int(Bat_Charge_Warn)]

    Bat_Charge = format_to_text.Get_NUT_Variable(UPS, 'battery.charge')
    if Bat_Charge:
        Bat_Charge = float(Bat_Charge)
        Result['bat_charge'] = [int(Bat_Charge), 100 - int(Bat_Charge)]
    return

# ==========================================================
# Dougnut graphics - Dougnut_Battery_Voltage
# ==========================================================
def Dougnut_Battery_Voltage(UPS, Result):
    Result['bat_volts']   = [0, 1]
    Result['bat_v_scale'] = [1, 0, 0, 0, 0]
    Result['bat_v_nom']   = [0, 0, 0]

    Bat_Volts_Max = 14.5
    Bat_Volts_Nom = format_to_text.Get_NUT_Variable(UPS, 'battery.voltage.nominal')
    if Bat_Volts_Nom:
        Bat_Volts_Nom = float(Bat_Volts_Nom)
        Bat_Volts_Max = 1.2 * Bat_Volts_Nom
        Result['bat_v_nom'] = [float(Bat_Volts_Nom) - (Bat_Volts_Max / (Nominal_Width * 2)),
                   (Bat_Volts_Max / Nominal_Width),
                    Bat_Volts_Max - float(Bat_Volts_Nom) - (Bat_Volts_Max / (Nominal_Width * 2))]

    if Bat_Volts_Low := format_to_text.Get_NUT_Variable(UPS, 'battery.voltage.low'):
        Bat_Volts_Low = float(Bat_Volts_Low)
        Result['bat_v_scale'] = [0, 0, Bat_Volts_Low, (Bat_Volts_Max - Bat_Volts_Low) * 0.25,
                                 (Bat_Volts_Max - Bat_Volts_Low) * 0.75]
    else:
        if Bat_Volts_Nom:
            Result['bat_v_scale'] = [0, 0, Bat_Volts_Nom * 0.82,
                                     Bat_Volts_Nom * 0.08, Bat_Volts_Nom * 0.3]

    if Bat_Volts_Max == 0:
        Bat_Volts_Max = 0.1
    if Bat_Volts := format_to_text.Get_NUT_Variable(UPS, 'battery.voltage'):
        Bat_Volts = float(Bat_Volts)
        Result['bat_volts'] = [Bat_Volts, Bat_Volts_Max - Bat_Volts]
    return

# ==========================================================
# Dougnut graphics - Dougnut_Output_Power
# ==========================================================
def Dougnut_Output_Power(UPS, Result):
    Result['power_out']       = [0, 1, 0]
    Result['power_out_scale'] = [0, 0, 100, 10]
    Power_Watts = '--'

    if UPS_Load := format_to_text.Get_NUT_Variable(UPS, 'ups.load'):
        UPS_Load = float(UPS_Load)

        Realpower_Nom = format_to_text.Get_NUT_Variable(UPS, 'ups.realpower.nominal')
        if Device := configuration.Get_Device(UPS['server_address'], UPS['name']):
            if 'power' in Device:
                Realpower_Nom = Device['power']

        if Realpower_Nom:
            Power_Watts = int(float(Realpower_Nom) * (UPS_Load / 100))
        else:
            Power_Watts = 0

        Result['power_out'] = [int(UPS_Load), 110 - int(UPS_Load), Power_Watts]
    return

# ==========================================================
# region Charts
# Chart_Input_Voltage
# ==========================================================
def Chart_Input_Voltage(UPS, Result):
    Target_Device = UPS['name'] + "_" + UPS['server_address']
    Vin_Y = session[Target_Device]['in_volt_y']

    if Input_Volts := format_to_text.Get_NUT_Variable(UPS, 'input.voltage'):
        Input_Volts = float(Input_Volts)
    else:
        Input_Volts = 0

    Vin_Y.append(Input_Volts)
    Vin_Y.pop(0)
    Result['in_volt_y'] = Vin_Y
    session[Target_Device]['in_volt_y'] = Vin_Y

    # ==========================================================
    # Select a minumum range for the Y axis
    # ==========================================================
    Result['in_volt_min'] = Result['in_volt_max'] = 'null'

    if current_app.config['UI']['AUTORANGE_VIN']:
        Min_Range = current_app.config['UI']['MIN_RANGE_VIN']
        Data_Max = max(Clean_List(Vin_Y))
        Data_Min = min(Clean_List(Vin_Y))
        Data_Range = Data_Max - Data_Min
        if Data_Range < Min_Range:
            Pad = (Min_Range - Data_Range) / 2
            if (Data_Min - Pad) < 0:
                Result['in_volt_min'] = 0
                Pad = Pad + (Data_Min - Pad)
            else:
                Result['in_volt_min'] = Data_Min - Pad
            Result['in_volt_max'] = Data_Max + Pad

    return

# ==========================================================
# Chart graphics - Chart_Battery_Charge
# ==========================================================
def Chart_Battery_Charge(UPS, Result):
    Target_Device = UPS['name'] + "_" + UPS['server_address']
    Charge_Y = session[Target_Device]['bat_ch_y']

    if not (Bat_Charge := format_to_text.Get_NUT_Variable(UPS, 'battery.charge')):
        Bat_Charge = 0

    Bat_Charge = float(Bat_Charge)
    Charge_Y.append(int(Bat_Charge))
    Charge_Y.pop(0)
    Result['bat_ch_y'] = Charge_Y
    session[Target_Device]['bat_ch_y'] = Charge_Y
    return

# ==========================================================
# Chart graphics - Chart_Output_Power
# ==========================================================
def Chart_Output_Power(UPS, Result):
    Target_Device = UPS['name'] + "_" + UPS['server_address']
    Power_Y = session[Target_Device]['out_power_y']

    if not (UPS_Load := format_to_text.Get_NUT_Variable(UPS, 'ups.load')):
        UPS_Load = 0

    UPS_Load = float(UPS_Load)
    Power_Y.append(UPS_Load)
    Power_Y.pop(0)
    Result['out_power_y'] = Power_Y
    session[Target_Device]['out_power_y'] = Power_Y

    # ==========================================================
    # Select a minumum range for the Y axis
    # ==========================================================
    Result['out_power_y_min'] = 0
    Result['out_power_y_max'] = 100
    if current_app.config['UI']['AUTORANGE_POW']:
        Min_Range  = current_app.config['UI']['MIN_RANGE_POW']
        Data_Max   = max(Clean_List(Power_Y))
        Data_Min   = min(Clean_List(Power_Y))
        Data_Range = Data_Max - Data_Min
        if Data_Range < Min_Range:
            Pad = (Min_Range - Data_Range) / 2
            if (Data_Min - Pad) < 0:
                Result['out_power_y_min'] = 0
                Pad = Pad + (Data_Min - Pad)
            else:
                Result['out_power_y_min'] = Data_Min - Pad
            Result['out_power_y_max'] = Data_Max + Pad

    # ==========================================================
    # Set Watts scale
    # ==========================================================
    Realpower_Nom = format_to_text.Get_NUT_Variable(UPS, 'ups.realpower.nominal')

    if Device := configuration.Get_Device(UPS['server_address'], UPS['name']):
        if 'power' in Device:
            Realpower_Nom = Device['power']
            current_app.logger.debugv(
                "Chart_Output_Power: Using power value from config {}".format(
                    Realpower_Nom))

    if Realpower_Nom:
        Result['out_power_watts_max'] = int(
            float(Realpower_Nom) * float(Result['out_power_y_max']) / 100)
        Result['out_power_watts_min'] = int(
            float(Realpower_Nom) * float(Result['out_power_y_min']) / 100)
    else:
        Result['out_power_watts_max'] = 1
        Result['out_power_watts_min'] = 0

    return

# ==========================================================
# Chart graphics - Chart_Runtime
# ==========================================================
def Chart_Runtime(UPS, Result):
    Target_Device = UPS['name'] + "_" + UPS['server_address']
    Runtime_Y = session[Target_Device]['runtime_y']

    if not (Runtime := format_to_text.Get_NUT_Variable(UPS, 'battery.runtime')):
        Runtime = 0

    if Runtime:
        Runtime_Y.append(float(Runtime) / 60.0)
        Runtime_Y.pop(0)
    Result['runtime_y'] = Runtime_Y
    session[Target_Device]['runtime_y'] = Runtime_Y

    if current_app.config['UI']['AUTORANGE_RUN']:
        Min_Range  = current_app.config['UI']['MIN_RANGE_RUN']
        Data_Max   = max(Clean_List(Runtime_Y))
        Data_Min   = min(Clean_List(Runtime_Y))
        Data_Range = Data_Max - Data_Min
        if Data_Range < Min_Range:
            Pad = (Min_Range - Data_Range) / 2

            if (Data_Min - Pad) < 0:
                Result['runtime_y_min'] = 0
                Pad = Pad + (Data_Min - Pad)
            else:
                Result['runtime_y_min'] = Data_Min - Pad

            Result['runtime_y_max'] = Data_Max + Pad
    return

# =============================================================================
# region Others
# Process_Runtime_Block -
# =============================================================================
def Process_Runtime_Block(UPS, Result):
    if Runtime := format_to_text.Get_NUT_Variable(UPS, 'battery.runtime'):
        Runtime = float(Runtime)
        Formatted_Time = time.strftime(current_app.config["UI"]["FORMAT_RUNTIME"],
                                       time.gmtime(int(Runtime)))
    else:
        Formatted_Time = 'Not Found'

    Runtime_Format = "main-data"
    if Runtime_Low := format_to_text.Get_NUT_Variable(UPS, 'battery.runtime.low'):
        if int(Runtime) < int(Runtime_Low):
            Runtime_Format = "main-data-danger"
    Result['runtime'] = Runtime_HTML.format(time=Formatted_Time, fmt=Runtime_Format)
    return

# =============================================================================
# Process_Sounder_Block -
# =============================================================================
def Process_Sounder_Block(UPS, Result):
    Sounder_Text = 'Unknown'
    s_muted = s_disabled = s_enabled = ''
    if Sounder_State := format_to_text.Get_NUT_Variable(UPS, 'ups.beeper.status'):
        if Sounder_State.lower() == 'enabled':
            Sounder_Text = "Enabled"
            s_enabled = 'active'
        elif Sounder_State.lower() == 'disabled':
            Sounder_Text = "Disabled"
            s_disabled = 'active'
        elif Sounder_State.lower() == 'muted':
            Sounder_Text = "Muted"
            s_muted = 'active'

    # =========================================================================
    # Use ups.beeper.status.text if present (usually only when in APC mode)
    # =========================================================================
    if Beep_Status_Text := format_to_text.Get_NUT_Variable(UPS, 'ups.beeper.status.text'):
        Sounder_Text = Beep_Status_Text

    Result['sounder'] = Sounder_HTML.format(
                            state=Sounder_Text,
                            s_muted= s_muted,
                            s_disabled= s_disabled,
                            s_enabled= s_enabled
                             )
    return

# =============================================================================
# Get_Bat_Charge_State - Util to get a state for the battery charge
# Returns:
#   0 - Unknown
#   1 - Low
#   2 - Partial
#   3 - Almost full
#   4 - Full
# =============================================================================
def Get_Bat_Charge_State(UPS):
    State = 0
    # Return value  0   1   2   3    4
    Thresholds = [-1, 25, 50, 94, 100]

    # ==========================================================
    # Get values to update the default thresholds
    # ==========================================================
    if Bat_Charge := format_to_text.Get_NUT_Variable(UPS, 'battery.charge'):
        try:
            Bat_Charge = float(Bat_Charge)
        except Exception:
            Bat_Charge = None
        if Bat_Charge:
            if Bat_Charge_Low := format_to_text.Get_NUT_Variable(UPS, 'battery.charge.low'):
                try:
                    Bat_Charge_Low = float(Bat_Charge_Low)
                except Exception:
                    Bat_Charge_Low = None

            if Bat_Charge_Warn := format_to_text.Get_NUT_Variable(UPS, 'battery.charge.warning'):
                try:
                    Bat_Charge_Warn = float(Bat_Charge_Warn)
                except Exception:
                    Bat_Charge_Warn = None

    # ==========================================================
    # Update the default thresholds if we have information
    # ==========================================================
            if Bat_Charge_Low and Bat_Charge_Warn:
                Thresholds[1] = Bat_Charge_Low
                Thresholds[2] = Bat_Charge_Warn
            elif Bat_Charge_Low and not Bat_Charge_Warn:
                Thresholds[1] = Bat_Charge_Low
                Thresholds[2] = ((100 - Bat_Charge_Low) / 2) + Bat_Charge_Low
            elif not Bat_Charge_Low and Bat_Charge_Warn:
                Thresholds[1] = Bat_Charge_Warn
                Thresholds[2] = ((100 - Bat_Charge_Warn) / 2) + Bat_Charge_Warn

    # ==========================================================
    # Map the battery charge to a return value
    # ==========================================================
            State = min(range(len(Thresholds)), key=lambda x: (Bat_Charge - Thresholds[x]) > 0)
    return State

# =============================================================================
# Process_Status_Block -
# =============================================================================
def Process_Status_Block(UPS, Result):
    # ==========================================================
    # Status block
    Status_Text           = 'Unknown'
    Secondary_Text        = ''

    Line_Icon             = Icon_Line
    Line_Icon_Style       = 'text-secondary text-muted'
    Line_Icon_Tip         = 'Line OK'

    Line_Alert_Icon       = Icon_Unknown  # Icon_Check
    Line_Alert_Icon_Style = 'text-success'
    Line_Alert_Tip        = 'Line OK'

    Battery_Icon          = Icon_Bat_Empty
    Battery_Icon_Style    = 'text-secondary text-muted'
    Battery_Icon_Tip      = 'Battery OK'

    Battery_Alert_Icon       = Icon_Check
    Battery_Alert_Icon_Style = 'text-success'
    Battery_Alert_Tip        = 'Battery OK'

    # ==========================================================
    # Status block - server ID
    Server = configuration.Get_Server(UPS['server_address'])

    if Server:
        if 'name' in Server:
            Server_Name = Server['name']
            Result['server_summary'] = Server_Name + "&nbsp(" + UPS['server_address'] \
                  + "&nbsp-&nbsp" + UPS['name'] + ")"
        else:
            Result['server_summary'] = UPS['server_address'] \
                + "&nbsp-&nbsp" + UPS['name']

    # ==========================================================
    # Status block
    Status_Var = format_to_text.Get_NUT_Variable(UPS, 'ups.status')
    if Status_Var:
        Status_Var = Status_Var.upper()
        Search_List = re.split(r' |:|;|-|\.|/|\\', Status_Var)
        current_app.logger.debugv("Status message: {}".format(Search_List))

        # ==========================================================
        # Process line information
        # ==========================================================
        if 'OL' in Search_List:
            Status_Text     = "On-Line"

            Line_Icon_Style = 'text-success'
            Line_Icon_Tip   = 'On-Line, Power OK'

            Line_Alert_Icon       = Icon_Vin_Normal
            Line_Alert_Icon_Style = 'text-success'
            Line_Alert_Tip        = 'Voltage Within Limits'
        else:
            Line_Icon_Style = 'text-danger'
            Line_Icon_Tip   = 'Off-Line, Power Missing'

            Line_Alert_Icon_Style = 'text-warning'
            Line_Alert_Icon = Icon_Alert_Triangle
            Line_Alert_Tip = 'Off-Line, Power Missing'

        if 'BOOST' in Search_List:
            Status_Text     += " Battery Boosting"

            Line_Icon_Style = 'text-warning'
            Line_Icon_Tip   = "Low Line Level, Boosting Input"

            Line_Alert_Icon_Style = 'text-warning'
            Line_Alert_Icon       = Icon_Vin_Boost
            Line_Alert_Tip        = "Low Line Level"

        if 'TRIM' in Search_List:
            Status_Text     += " Trim Line"

            Line_Icon_Style = 'text-warning'
            Line_Icon_Tip   = "Trimming Line Level"

            Line_Alert_Icon       = Icon_Vin_Trim
            Line_Alert_Icon_Style = 'text-warning'
            Line_Alert_Tip        = "Line Level High, Trimming Input"

        # ==========================================================
        # Process battery information
        # ==========================================================
        Battery_Charge_State = Get_Bat_Charge_State(UPS)
        BI_Charge_Lookup   = [Icon_Bat_Empty, Icon_Bat_Empty,  Icon_Bat_Half,          Icon_Bat_Half, Icon_Bat_Full]  # noqa: E501
        BIS_Charge_Lookup  = [ 'text-danger',  'text-danger', 'text-warning',         'text-warning',   'text-info']  # noqa: E501

        BAI_Charge_Lookup  = [ Icon_Unknown, Icon_Error_Octagon, Icon_Alert_Triangle,    Icon_Alert_Triangle,     Icon_Check]  # noqa: E501
        BAIS_Charge_Lookup = ['text-danger',      'text-danger',       'text-danger',         'text-warning', 'text-success']  # noqa: E501
        BAIT_Charge_Lookup = [    'Unknown',            'Empty',               'Low', 'Partially discharged',         'Full']  # noqa: E501

        if 'OB' in Search_List:
            Status_Text        = "On-Battery"
            Secondary_Text     = "Discharging"

            Battery_Icon       = BI_Charge_Lookup[Battery_Charge_State]
            Battery_Icon_Style = BIS_Charge_Lookup[Battery_Charge_State]
            Battery_Icon_Tip   = 'On-Battery, Discharging'

            Battery_Alert_Icon       = BAI_Charge_Lookup[Battery_Charge_State]
            Battery_Alert_Icon_Style = BAIS_Charge_Lookup[Battery_Charge_State]
            Battery_Alert_Tip        = BAIT_Charge_Lookup[Battery_Charge_State]
        else:
            if 'CHRG' in Search_List:
                Secondary_Text           = "Charging"
                Battery_Icon             = Icon_Bat_Charging
                Battery_Icon_Style       = BIS_Charge_Lookup[Battery_Charge_State]
                Battery_Icon_Tip         = 'Battery Charging'

                Battery_Alert_Icon       = BAI_Charge_Lookup[Battery_Charge_State]
                Battery_Alert_Icon_Style = BAIS_Charge_Lookup[Battery_Charge_State]
                Battery_Alert_Tip        = BAIT_Charge_Lookup[Battery_Charge_State]
            else:
                Battery_Icon             = BI_Charge_Lookup[Battery_Charge_State]
                Battery_Icon_Style       = BIS_Charge_Lookup[Battery_Charge_State]
                Battery_Icon_Tip         = 'OK'

                Battery_Alert_Icon       = BAI_Charge_Lookup[Battery_Charge_State]
                Battery_Alert_Icon_Style = BAIS_Charge_Lookup[Battery_Charge_State]
                Battery_Alert_Tip        = BAIT_Charge_Lookup[Battery_Charge_State]

        if 'LB' in Search_List:
            Status_Text     = "On-Battery"
            Secondary_Text += " Low battery"

            Battery_Icon             = BI_Charge_Lookup[2]
            Battery_Icon_Style       = BIS_Charge_Lookup[2]
            Battery_Icon_Tip         = 'Battery low'

            Battery_Alert_Icon       = BAI_Charge_Lookup[2]
            Battery_Alert_Icon_Style = BAIS_Charge_Lookup[2]
            Battery_Alert_Tip        = BAIT_Charge_Lookup[2]

        if 'RB' in Search_List:
            Secondary_Text += " Replace battery"

            Battery_Icon             = Icon_Bat_Empty
            Battery_Icon_Style       = 'text-danger'
            Battery_Icon_Tip         = 'Battery is EOL'

            Battery_Alert_Icon       = Icon_Error_Octagon
            Battery_Alert_Icon_Style = 'text-danger'
            Battery_Alert_Tip        = 'Battery is EOL'

    Result['status'] = Status_HTML.format(
        status_text             = Status_Text,
        secondary_text          = Secondary_Text,

        line_icon               = Line_Icon,
        line_icon_style         = Line_Icon_Style,
        line_icon_tip           = Line_Icon_Tip,

        line_alert_icon         = Line_Alert_Icon,
        line_alert_icon_style   = Line_Alert_Icon_Style,
        line_alert_tip          = Line_Alert_Tip,

        battery_icon            = Battery_Icon,
        bat_icon_style          = Battery_Icon_Style,
        bat_icon_tip            = Battery_Icon_Tip,

        bat_alert_icon          = Battery_Alert_Icon,
        bat_alert_style         = Battery_Alert_Icon_Style,
        bat_alert_tip           = Battery_Alert_Tip,
   )

    # ==========================================================
    # Status block drop down
    Result['ups_status'] = Status_Var

    Result['ups_temp'] = "Not Present"
    if UPS_Temp := format_to_text.Get_NUT_Variable(UPS, 'ups.temperature'):
        Result['ups_temp'] = UPS_Temp + "&deg;C (UPS)"
    elif UPS_Temp := format_to_text.Get_NUT_Variable(UPS, 'battery.temperature'):
        Result['ups_temp'] = UPS_Temp + "&deg;C (Bat)"

    if APC_Status := format_to_text.Get_NUT_Variable(UPS, 'STATUS'):
        Result['apc_status'] = APC_Status
    else:
        Result['apc_status'] = "Not Present"

    if APC_BCharge := format_to_text.Get_NUT_Variable(UPS, 'BCHARGE'):
        Result['apc_bcharge'] = APC_BCharge
    else:
        Result['apc_bcharge'] = "Not Present"

    if APC_StatFlag := format_to_text.Get_NUT_Variable(UPS, 'STATFLAG'):
        Result['apc_statflag'] = APC_StatFlag
    else:
        Result['apc_statflag'] = "Not Present"

    if UPS_Model := format_to_text.Get_NUT_Variable(UPS, 'ups.model'):
        Result['ups_model'] = UPS_Model
    else:
        Result['ups_model'] = "Not Present"

    # ==========================================================
    # Client list
    if 'clients' in UPS:
        if len(UPS['clients']) == 0:
            Result['client_cnt'] = 'None'
            Result['client_list'] = '-----'
        else:
            Result['client_cnt'] = len(UPS['clients'])
            Result['client_list'] = ''
            for Client in UPS['clients']:
                Result['client_list'] += Client + "<br>"
    else:
        Result['client_cnt'] = 'None'
        Result['client_list'] = '-----'

    return

# =============================================================================
# Process_Device_Pulldown -
# =============================================================================
def Process_Device_Pulldown(Addr, Device, Result):
    Result['device_menu'] = ""

    for svr in current_app.config['SERVERS']:
        for dev in svr['devices']:
            if 'default' in dev:
                Def_Style = 'text-warning'
            else:
                Def_Style = 'd-none'

            if Addr == svr['server'] and Device == dev['device']:
                Active_Item = 'active'
            else:
                Active_Item = ''

            Mode_Query = '&mode=nut'
            Mode_Text  = ' (NUT)'
            if 'mode' in svr:
                if svr['mode'].lower() == 'apc':
                    Mode_Query = '&mode=apc'
                    Mode_Text  = ' (APC)'

            if 'displayname' in dev:
                Addr_Name = dev['displayname']
                Dev_Name = ''
            else:
                Addr_Name = svr['server']
                Dev_Name = dev['device']

            Result['device_menu'] += Device_Pulldown_HTML.format(
                addr      = svr['server'],
                dev       = dev['device'],
                addr_name = Addr_Name,
                dev_name  = Dev_Name,
                mode      = Mode_Text,
                mode_q    = Mode_Query,
                def_style = Def_Style,
                active    = Active_Item
            )
    return Result

# =============================================================================
# Process_Download_Pulldown -
# =============================================================================
def Process_Download_Pulldown(UPS, Result, Mode):
    Result['download_menu'] = ""

    Formats = [
        {'name': 'Metrics',  'path': 'metrics', 'dl_opt': 'false'},
        {'name': 'JSON',     'path': 'json',    'dl_opt': 'false'},
        {'name': 'Raw JSON', 'path': 'raw',     'dl_opt': 'false'},
        {'name': 'HR'},
        {'name': 'Metrics',  'path': 'metrics', 'dl_opt': 'true'},
        {'name': 'JSON',     'path': 'json',    'dl_opt': 'true'},
        {'name': 'Raw JSON', 'path': 'raw',     'dl_opt': 'true'},
   ]

    if Mode == 'apc':
        Mode_q = "&mode={}".format(Mode)
    else:
        Mode_q = ""

    Result['download_menu'] += '<div class="dropdown-item disabled">View</div>'
    for opt in Formats:
        if opt['name'] == "HR":
            Result['download_menu'] += '<div class="dropdown-divider"></div>'
            Result['download_menu'] += '<div class="dropdown-item disabled">Download</div>'
        else:
            Result['download_menu'] += Download_Pulldown_HTML.format(
                path      = opt['path'],
                addr      = UPS['server_address'],
                dev       = UPS['name'],
                mode_q    = Mode_q,
                fmt       = opt['name'],
                dl_opt    = opt['dl_opt'],
               )
    return

# =============================================================================
# Process_Download_Pulldown -
# =============================================================================
def Generate_Log_Files_Pulldown(Directory):
    Menu_HTML = ""
    Max_Files = current_app.config['UI']["LOGFILES_LIST"]

    Files = os.listdir(Directory)

    if len(Files) == 0:
        Menu_HTML = "No files found"
    else:
        File_List = []

        for f in Files:
            Full_Name = os.path.join(Directory, f)
            if os.path.isdir(Full_Name):
                continue

            File_Age = time.time() - os.path.getmtime(Full_Name)
            Age_String = arrow.get(os.path.getmtime(Full_Name)).humanize(arrow.utcnow(),
                                                only_distance=True) + " ago"
            if Age_String == 'instantly ago':
                Age_String = 'Now'

            File_List.append({ 'Name': f, 'Age': File_Age, 'AgeString': Age_String})

        # Prepare the list by sorting by recently modified first
        File_List = sorted(File_List, key=lambda x: x['Age'])

        # Limit the number of entries on the list
        if len(File_List) > Max_Files:
            File_List = File_List[0:Max_Files]

        for e in File_List:
            Menu_HTML += Log_File_Pulldown_HTML.format(
                file      = e['Name'],
                note      = e['AgeString']
               )

    return Menu_HTML

# =============================================================================
# region Main
# Process_Data_For_GUI -
# =============================================================================
def Process_Data_For_GUI(Scrape_Data, Device):
    Result = {}

    if Scrape_Data['mode'] == "apc":  # scrape.Server_Protocol.APC:
        apc_to_nut.Translate_APC_To_NUT(Scrape_Data)

    # ==========================================================
    #  X-Axis & Default stuff
    # ==========================================================
    Length = current_app.config['CHART_SAMPLES']
    Result['time_axis_data'] = Time_Axis_Array(Length)
    Result['server_version'] = Scrape_Data['server_version']

    # ==========================================================
    # Get the UPS dictionary from the raw structure
    # ==========================================================
    UPS = format_to_text.Get_UPS(Scrape_Data, Device)
    current_app.logger.debugv(
        "Process_Data_For_GUI: UPS dictionary {} target Device {}".format(UPS, Device))
    if not UPS:
        current_app.logger.warning("Could not find device {} in scrape data".format(Device))
        return {}
    else:
        current_app.logger.debugv("Found device {} in scrape data".format(Device))

    # ==========================================================
    # Initialise space for the chart data if it's not present
    # ==========================================================
    if 'touch' not in session:
        session['touch'] = False
    session['touch'] = not session['touch']

    Target_Device = UPS['name'] + "_" + UPS['server_address']
    if (Target_Device not in session):
        Length = current_app.config['CHART_SAMPLES']
        Empty_List = ['null' for i in range(Length)]
        session[Target_Device] = {}
        session[Target_Device]['bat_ch_y'] = Empty_List.copy()
        session[Target_Device]['in_volt_y'] = Empty_List.copy()
        session[Target_Device]['out_power_y'] = Empty_List.copy()
        session[Target_Device]['runtime_y'] = Empty_List.copy()

    # ==========================================================
    # Status block
    # ==========================================================
    Process_Download_Pulldown(UPS, Result, Scrape_Data['mode'])
    Process_Status_Block(UPS, Result)
    Process_Runtime_Block(UPS, Result)
    Process_Sounder_Block(UPS, Result)

    # ==========================================================
    # Dougnut graphics
    # ==========================================================
    Dougnut_Input_Voltage(UPS, Result)
    Dougnut_Battery_Charge(UPS, Result)
    Dougnut_Battery_Voltage(UPS, Result)
    Dougnut_Output_Power(UPS, Result)

    # ==========================================================
    # Chart graphics
    # ==========================================================
    Chart_Input_Voltage(UPS, Result)
    Chart_Battery_Charge(UPS, Result)
    Chart_Output_Power(UPS, Result)
    Chart_Runtime(UPS, Result)

    return Result
