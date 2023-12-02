from enum import Enum

#=======================================================================
# Enumerated types & constants
#=======================================================================
Variable_Format = Enum('Variable_Format', ['NONE', 'PERCENTAGE', 'BEEPERSTATUS', 'OLDUPSSTATUS'])
Variable_Type = Enum('Variable_Type', ['NONE', 'INTEGER', 'FLOAT', 'STRING'])

#=======================================================================
# Metric descriptions
#=======================================================================
Metric_Data_List = [
    {
        "nut_var":  "",
        "metric":   "nut_exporter_info",
        "help":     "Metadata about the exporter.",
        "unit":     "",
        "style":    "info",
        "type":     Variable_Type.INTEGER,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "",
        "metric":   "nut_server_info",
        "help":     "Metadata about the NUT server.",
        "unit":     "",
        "style":    "info",
        "type":     Variable_Type.INTEGER,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "",
        "metric":   "nut_ups_info",
        "help":     "Metadata about the UPS.",
        "unit":     "",
        "style":    "info",
        "type":     Variable_Type.INTEGER,
        "format":   Variable_Format.NONE
    },
# Depricated
    {
        "nut_var":  "",
        "metric":   "nut_info",
        "help":     "Metadata about the NUT server. (Deprecated, use nut_server_info instead.)",
        "unit":     "",
        "style":    "info",
        "type":     Variable_Type.INTEGER,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "ups.status",
        "metric":   "nut_ups_status",
        "help":     "UPS status. Check for a specific status with the \"status\" label.",
        "unit":     "",
        "style":    "stateset",
        "type":     Variable_Type.NONE,
        "format":   Variable_Format.NONE
    },
# Variable metrics
    {
        "nut_var":  "ups.beeper.status",
        "metric":   "nut_beeper_status",
        "help":     "If the beeper is enabled. Unknown (0), enabled (1), disabled (2) or muted (3).",
        "unit":     "",
        "style":    "gauge",
        "type":     Variable_Type.INTEGER,
        "format":   Variable_Format.BEEPERSTATUS
    },
    {
        "nut_var":  "device.uptime",
        "metric":   "nut_uptime_seconds",
        "help":     "Device uptime.",
        "unit":     "seconds",
        "style":    "gauge",
        "type":     Variable_Type.INTEGER,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "ups.load",
        "metric":   "nut_load",
        "help":     "Load. (0-1)",
        "unit":     "",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.PERCENTAGE
    },
    {
        "nut_var":  "ups.temperature",
        "metric":   "nut_temperature_celsius",
        "help":     "UPS temperature",
        "unit":     "celsius",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
# Battery
    {
        "nut_var":  "battery.charge",
        "metric":   "nut_battery_charge",
        "help":     "Battery level. (0-1)",
        "unit":     "",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.PERCENTAGE
    },
    {
        "nut_var":  "battery.charge.low",
        "metric":   "nut_battery_charge_low",
        "help":     "Battery level threshold for low state. (0-1)",
        "unit":     "",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.PERCENTAGE
    },
    {
        "nut_var":  "battery.charge.warning",
        "metric":   "nut_battery_charge_warning",
        "help":     "Battery level threshold for warning state. (0-1)",
        "unit":     "",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.PERCENTAGE
    },
    {
        "nut_var":  "battery.charge.restart",
        "metric":   "nut_battery_charge_restart",
        "help":     "Battery level threshold for restarting after power-off. (0-1)",
        "unit":     "",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.PERCENTAGE
    },
    {
        "nut_var":  "battery.runtime",
        "metric":   "nut_battery_runtime_seconds",
        "help":     "Battery runtime.",
        "unit":     "seconds",
        "style":    "gauge",
        "type":     Variable_Type.INTEGER,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "battery.runtime.low",
        "metric":   "nut_battery_runtime_low_seconds",
        "help":     "Battery runtime threshold for state low.",
        "unit":     "seconds",
        "style":    "gauge",
        "type":     Variable_Type.INTEGER,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "battery.runtime.restart",
        "metric":   "nut_battery_runtime_restart_seconds",
        "help":     "Battery runtime threshold for restart after power-off.",
        "unit":     "seconds",
        "style":    "gauge",
        "type":     Variable_Type.INTEGER,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "ups.delay.shutdown",
        "metric":   "nut_delay_shutdown_seconds",
        "help":     "Interval to wait after shutdown with delay command.",
        "unit":     "seconds",
        "style":    "gauge",
        "type":     Variable_Type.INTEGER,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "ups.delay.start",
        "metric":   "nut_delay_start_seconds",
        "help":     "Interval to wait before (re)starting the load.",
        "unit":     "seconds",
        "style":    "gauge",
        "type":     Variable_Type.INTEGER,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "battery.voltage",
        "metric":   "nut_battery_voltage_volts",
        "help":     "Battery voltage.",
        "unit":     "volts",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "battery.voltage.nominal",
        "metric":   "nut_battery_voltage_nominal_volts",
        "help":     "Battery voltage (nominal).",
        "unit":     "volts",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "battery.voltage.high",
        "metric":   "nut_battery_voltage_high_volts",
        "help":     "Battery voltage for full (charge level calculation).",
        "unit":     "volts",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "battery.voltage.low",
        "metric":   "nut_battery_voltage_low_volts",
        "help":     "Battery voltage for empty (charge level calculation).",
        "unit":     "volts",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
# Input
    {
        "nut_var":  "battery.temperature",
        "metric":   "nut_battery_temperature_celsius",
        "help":     "Battery temperature.",
        "unit":     "celsius",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "input.voltage",
        "metric":   "nut_input_voltage_volts",
        "help":     "Input voltage.",
        "unit":     "volts",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "input.voltage.nominal",
        "metric":   "nut_input_voltage_nominal_volts",
        "help":     "Input voltage (nominal).",
        "unit":     "volts",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "input.voltage.minimum",
        "metric":   "nut_input_voltage_minimum_volts",
        "help":     "Input voltage (minimum seen).",
        "unit":     "volts",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "input.voltage.maximum",
        "metric":   "nut_input_voltage_maximum_volts",
        "help":     "Input voltage (maximum seen).",
        "unit":     "volts",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "input.transfer.low",
        "metric":   "nut_input_transfer_low_volts",
        "help":     "Input lower transfer threshold.",
        "unit":     "volts",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "input.transfer.high",
        "metric":   "nut_input_transfer_high_volts",
        "help":     "Input upper transfer threshold.",
        "unit":     "volts",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "input.current",
        "metric":   "nut_input_current_amperes",
        "help":     "Input current.",
        "unit":     "amperes",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "input.current.nominal",
        "metric":   "nut_input_current_nominal_amperes",
        "help":     "Input current (nominal).",
        "unit":     "amperes",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "input.frequency",
        "metric":   "nut_input_frequency_hertz",
        "help":     "Input frequency.",
        "unit":     "hertz",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "input.frequency.nominal",
        "metric":   "nut_input_frequency_nominal_hertz",
        "help":     "Input frequency (nominal).",
        "unit":     "hertz",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "input.frequency.low",
        "metric":   "nut_input_frequency_low_hertz",
        "help":     "Input frequency (low).",
        "unit":     "hertz",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "input.frequency.high",
        "metric":   "nut_input_frequency_high_hertz",
        "help":     "Input frequency (high).",
        "unit":     "hertz",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "output.voltage",
        "metric":   "nut_output_voltage_volts",
        "help":     "Output voltage.",
        "unit":     "volts",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "output.voltage.nominal",
        "metric":   "nut_output_voltage_nominal_volts",
        "help":     "Output voltage (nominal).",
        "unit":     "volts",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "output.current",
        "metric":   "nut_output_current_amperes",
        "help":     "Output current.",
        "unit":     "amperes",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "output.current.nominal",
        "metric":   "nut_output_current_nominal_amperes",
        "help":     "Output current (nominal).",
        "unit":     "amperes",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "output.frequency",
        "metric":   "nut_output_frequency_hertz",
        "help":     "Output frequency.",
        "unit":     "hertz",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
# Power
    {
        "nut_var":  "output.frequency.nominal",
        "metric":   "nut_output_frequency_nominal_hertz",
        "help":     "Output frequency (nominal).",
        "unit":     "hertz",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "ups.power",
        "metric":   "nut_power_watts",
        "help":     "Apparent power.",
        "unit":     "watts",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "ups.power.nominal",
        "metric":   "nut_power_nominal_watts",
        "help":     "Apparent power (nominal).",
        "unit":     "watts",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "ups.realpower",
        "metric":   "nut_real_power_watts",
        "help":     "Real power.",
        "unit":     "watts",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "ups.realpower.nominal",
        "metric":   "nut_real_power_nominal_watts",
        "help":     "Real power (nominal).",
        "unit":     "watts",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
# Metrics beyond here are deprecated
    {
        "nut_var":  "ups.status",
        "metric":   "nut_status",
        "help":     "UPS status. Unknown (0), on line (1, \"OL\"), on battery (2, \"OB\"), or low battery (3, \"LB\"). (Deprecated, use nut_ups_status instead.)",
        "unit":     "",
        "style":    "gauge",
        "type":     Variable_Type.INTEGER,
        "format":   Variable_Format.OLDUPSSTATUS
    },
    {
        "nut_var":  "battery.voltage",
        "metric":   "nut_battery_volts",
        "help":     "Battery voltage. (Deprecated, use nut_battery_voltage_volts instead.)",
        "unit":     "volts",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "input.voltage",
        "metric":   "nut_input_volts",
        "help":     "Input voltage. (Deprecated, use nut_input_voltage_volts instead.)",
        "unit":     "volts",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    },
    {
        "nut_var":  "output.voltage",
        "metric":   "nut_output_volts",
        "help":     "Output voltage. (Deprecated, use nut_output_voltage_volts instead.)",
        "unit":     "volts",
        "style":    "gauge",
        "type":     Variable_Type.FLOAT,
        "format":   Variable_Format.NONE
    }
]
