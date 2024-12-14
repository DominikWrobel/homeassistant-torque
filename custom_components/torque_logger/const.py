"""Constants for Torque Logger"""
# Base component constants
from typing import Final
import json
import os

NAME: Final = "Torque Logger"
DOMAIN: Final = "torque_logger"
_manifest = os.path.join(os.path.dirname(__file__), "manifest.json")
with open(_manifest, encoding="utf-8") as file:
    VERSION: Final = json.load(file)["version"]
ATTRIBUTION: Final = "Data provided by Torque Pro"
ISSUE_URL: Final = "https://github.com/junalmeida/homeassistant-torque/issues"

# CONF
CONF_EMAIL: Final = "email"
CONF_IMPERIAL: Final = "imperial"

# Platforms
DEVICE_TRACKER: Final = "device_tracker"
SENSOR: Final = "sensor"
PLATFORMS: Final = [SENSOR, DEVICE_TRACKER]

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""

# DEFAULTs
DEFAULT_ICON: Final = "mdi:engine"
GPS_ICON: Final = "mdi:car"
DISTANCE_ICON: Final = "mdi:map-marker-distance"
HIGHWAY_ICON: Final = "mdi:highway"
FUEL_ICON: Final = "mdi:gas-station"
TIME_ICON: Final = "mdi:clock"
CITY_ICON: Final = "mdi:city"
SPEED_ICON: Final = "mdi:speedometer"

# ATTR
ATTR_ALTITUDE: Final = "altitude"
ATTR_SPEED: Final = "speed"
ATTR_GPS_TIME: Final = "gps_time"

ENTITY_GPS: Final = "gps"

TORQUE_GPS_LAT: Final = "gpslat"
TORQUE_GPS_LON: Final = "gpslon"
TORQUE_GPS_ALTITUDE: Final = "gps_height"
TORQUE_GPS_ACCURACY: Final = "gps_acc"

# Webhook codes
TORQUE_CODES: Final = {
  "04": {
    "shortName": "engine_load",
    "fullName": "Engine Load",
    "unit": "%"
  },
  "05": {
    "shortName": "coolant_temp",
    "fullName": "Coolant Temperature",
    "unit": "°C"
  },
  "0c": {
    "shortName": "engine_rpm",
    "fullName": "Engine RPM",
    "unit": "rpm"
  },
  "0d": {
    "shortName": "speed",
    "fullName": "Vehicle Speed",
    "unit": "km/h"
  },
  "0f": {
    "shortName": "intake_temp",
    "fullName": "Intake Air Temperature",
    "unit": "°C"
  },
  "11": {
    "shortName": "throttle_pos",
    "fullName": "Throttle Position",
    "unit": "%"
  },
  "1f": {
    "shortName": "run_since_start",
    "fullName": "Distance Since Engine Start",
    "unit": "km"
  },
  "21": {
    "shortName": "dis_mil_on",
    "fullName": "Distance with MIL on",
    "unit": "km"
  },
  "2f": {
    "shortName": "fuel",
    "fullName": "Fuel Level",
    "unit": "%"
  },
  "31": {
    "shortName": "dis_mil_off",
    "fullName": "Distance with MIL off",
    "unit": "km"
  },
  "ff1001": {
    "shortName": "gps_spd",
    "fullName": "Vehicle Speed (GPS)",
    "unit": "km/h"
  },
  "ff1007": {
    "shortName": "gps_brng",
    "fullName": "GPS Bearing",
    "unit": "°"
  },
  "ff123a": {
    "shortName": "gps_sat",
    "fullName": "GPS Satellites",
    "unit": ""
  },
  "ff1010": {
    "shortName": TORQUE_GPS_ALTITUDE,
    "fullName": "GPS Altitude",
    "unit": "m"
  },
  "ff1006": {
    "shortName": TORQUE_GPS_LAT,
    "fullName": "GPS Latitude",
    "unit": "°"
  },
  "ff1239": {
    "shortName": TORQUE_GPS_ACCURACY,
    "fullName": "GPS Accuracy",
    "unit": "m"
  },
  "ff1237": {
    "shortName": "spd_diff",
    "fullName": "GPS vs OBD Speed difference",
    "unit": "km/h"
  },
  "ff1271": {
    "shortName": "fuel_used_trip",
    "fullName": "Fuel used (trip)",
    "unit": "litre"
  },
  "ff1005": {
    "shortName": TORQUE_GPS_LON,
    "fullName": "GPS Longitude",
    "unit": "°"
  },
  "47": {
    "shortName": "absolute_throttle_position_b",
    "fullName": "Absolute Throttle Position B",
    "unit": ""
  },
  "ff1223": {
    "shortName": "acceleration_sensor_total",
    "fullName": "Acceleration Sensor (Total)",
    "unit": ""
  },
  "ff1220": {
    "shortName": "acceleration_sensor_x_axis",
    "fullName": "Acceleration Sensor (X axis)",
    "unit": ""
  },
  "ff1221": {
    "shortName": "acceleration_sensor_y_axis",
    "fullName": "Acceleration Sensor (Y axis)",
    "unit": ""
  },
  "ff1222": {
    "shortName": "acceleration_sensor_z_axis",
    "fullName": "Acceleration Sensor (Z axis)",
    "unit": ""
  },
  "49": {
    "shortName": "accelerator_pedalposition_d",
    "fullName": "Accelerator PedalPosition D",
    "unit": ""
  },
  "4a": {
    "shortName": "accelerator_pedalposition_e",
    "fullName": "Accelerator PedalPosition E",
    "unit": ""
  },
  "4b": {
    "shortName": "accelerator_pedalposition_f",
    "fullName": "Accelerator PedalPosition F",
    "unit": ""
  },
  "ff124d": {
    "shortName": "air_fuel_ratio_commanded",
    "fullName": "Air Fuel Ratio (Commanded)",
    "unit": ""
  },
  "ff1249": {
    "shortName": "air_fuel_ratio_measured",
    "fullName": "Air Fuel Ratio (Measured)",
    "unit": ""
  },
  "12": {
    "shortName": "air_status",
    "fullName": "Air Status",
    "unit": ""
  },
  "46": {
    "shortName": "ambient_air_temp",
    "fullName": "Ambient air temp",
    "unit": ""
  },
  "ff1263": {
    "shortName": "average_trip_speed_whilst_moving_only",
    "fullName": "Average trip speed (whilst moving only)",
    "unit": ""
  },
  "ff1272": {
    "shortName": "average_trip_speed_whilst_stopped_or_moving",
    "fullName": "Average trip speed (whilst stopped or moving)",
    "unit": ""
  },
  "ff1270": {
    "shortName": "barometer_on_android_device",
    "fullName": "Barometer (on Android device)",
    "unit": ""
  },
  "33": {
    "shortName": "barometric_pressure_from_vehicle",
    "fullName": "Barometric pressure (from vehicle)",
    "unit": ""
  },
  "3c": {
    "shortName": "catalyst_temperature_bank_1_sensor_1",
    "fullName": "Catalyst Temperature (Bank 1 Sensor 1)",
    "unit": ""
  },
  "3e": {
    "shortName": "catalyst_temperature_bank_1_sensor_2",
    "fullName": "Catalyst Temperature (Bank 1 Sensor 2)",
    "unit": ""
  },
  "3d": {
    "shortName": "catalyst_temperature_bank_2_sensor_1",
    "fullName": "Catalyst Temperature (Bank 2 Sensor 1)",
    "unit": ""
  },
  "3f": {
    "shortName": "catalyst_temperature_bank_2_sensor_2",
    "fullName": "Catalyst Temperature (Bank 2 Sensor 2)",
    "unit": ""
  },
  "44": {
    "shortName": "commanded_equivalence_ratio_lambda",
    "fullName": "Commanded Equivalence Ratio (lambda)",
    "unit": ""
  },
  "ff126d": {
    "shortName": "cost_per_milekm_instant",
    "fullName": "Cost per mile/km (Instant)",
    "unit": ""
  },
  "ff126e": {
    "shortName": "cost_per_milekm_trip",
    "fullName": "Cost per mile/km (Trip)",
    "unit": ""
  },
  "ff1258": {
    "shortName": "co2_in_gkm_average",
    "fullName": "CO2 in g/km (Average)",
    "unit": ""
  },
  "ff1257": {
    "shortName": "co2_in_gkm_instantaneous",
    "fullName": "CO2 in g/km (Instantaneous)",
    "unit": ""
  },
  "ff126a": {
    "shortName": "distance_to_empty_estimated",
    "fullName": "Distance to empty (Estimated)",
    "unit": ""
  },
  "2c": {
    "shortName": "egr_commanded",
    "fullName": "EGR Commanded",
    "unit": ""
  },
  "2d": {
    "shortName": "egr_error",
    "fullName": "EGR Error",
    "unit": ""
  },
  "ff1273": {
    "shortName": "engine_kw_at_the_wheels",
    "fullName": "Engine kW (At the wheels)",
    "unit": ""
  },
  "43": {
    "shortName": "engine_load_absolute",
    "fullName": "Engine Load (Absolute)",
    "unit": ""
  },
  "5c": {
    "shortName": "engine_oil_temperature",
    "fullName": "Engine Oil Temperature",
    "unit": ""
  },
  "52": {
    "shortName": "ethanol_fuel_%",
    "fullName": "Ethanol Fuel %",
    "unit": ""
  },
  "32": {
    "shortName": "evap_system_vapour_pressure",
    "fullName": "Evap System Vapour Pressure",
    "unit": ""
  },
  "78": {
    "shortName": "exhaust_gas_temperature_1",
    "fullName": "Exhaust Gas Temperature 1",
    "unit": ""
  },
  "79": {
    "shortName": "exhaust_gas_temperature_2",
    "fullName": "Exhaust Gas Temperature 2",
    "unit": ""
  },
  "ff125c": {
    "shortName": "fuel_cost_trip",
    "fullName": "Fuel cost (trip)",
    "unit": ""
  },
  "ff125d": {
    "shortName": "fuel_flow_ratehour",
    "fullName": "Fuel flow rate/hour",
    "unit": ""
  },
  "ff125a": {
    "shortName": "fuel_flow_rateminute",
    "fullName": "Fuel flow rate/minute",
    "unit": ""
  },
  "0a": {
    "shortName": "fuel_pressure",
    "fullName": "Fuel pressure",
    "unit": ""
  },
  "23": {
    "shortName": "fuel_rail_pressure",
    "fullName": "Fuel Rail Pressure",
    "unit": ""
  },
  "22": {
    "shortName": "fuel_rail_pressure_relative_to_manifold_vacuum",
    "fullName": "Fuel Rail Pressure (relative to manifold vacuum)",
    "unit": ""
  },
  "ff126b": {
    "shortName": "fuel_remaining_calculated_from_vehicle_profile",
    "fullName": "Fuel Remaining (Calculated from vehicle profile)",
    "unit": ""
  },
  "03": {
    "shortName": "fuel_status",
    "fullName": "Fuel Status",
    "unit": ""
  },
  "07": {
    "shortName": "fuel_trim_bank_1_long_term",
    "fullName": "Fuel Trim Bank 1 Long Term",
    "unit": ""
  },
  "14": {
    "shortName": "fuel_trim_bank_1_sensor_1",
    "fullName": "Fuel trim bank 1 sensor 1",
    "unit": ""
  },
  "15": {
    "shortName": "fuel_trim_bank_1_sensor_2",
    "fullName": "Fuel trim bank 1 sensor 2",
    "unit": ""
  },
  "16": {
    "shortName": "fuel_trim_bank_1_sensor_3",
    "fullName": "Fuel trim bank 1 sensor 3",
    "unit": ""
  },
  "17": {
    "shortName": "fuel_trim_bank_1_sensor_4",
    "fullName": "Fuel trim bank 1 sensor 4",
    "unit": ""
  },
  "06": {
    "shortName": "fuel_trim_bank_1_short_term",
    "fullName": "Fuel Trim Bank 1 Short Term",
    "unit": ""
  },
  "09": {
    "shortName": "fuel_trim_bank_2_long_term",
    "fullName": "Fuel Trim Bank 2 Long Term",
    "unit": ""
  },
  "18": {
    "shortName": "fuel_trim_bank_2_sensor_1",
    "fullName": "Fuel trim bank 2 sensor 1",
    "unit": ""
  },
  "19": {
    "shortName": "fuel_trim_bank_2_sensor_2",
    "fullName": "Fuel trim bank 2 sensor 2",
    "unit": ""
  },
  "1a": {
    "shortName": "fuel_trim_bank_2_sensor_3",
    "fullName": "Fuel trim bank 2 sensor 3",
    "unit": ""
  },
  "1b": {
    "shortName": "fuel_trim_bank_2_sensor_4",
    "fullName": "Fuel trim bank 2 sensor 4",
    "unit": ""
  },
  "08": {
    "shortName": "fuel_trim_bank_2_short_term",
    "fullName": "Fuel Trim Bank 2 Short Term",
    "unit": ""
  },
  "ff123b": {
    "shortName": "gps_bearing",
    "fullName": "GPS Bearing",
    "unit": ""
  },
  "ff1226": {
    "shortName": "horsepower_at_the_wheels",
    "fullName": "Horsepower (At the wheels)",
    "unit": ""
  },
  "0b": {
    "shortName": "intake_manifold_pressure",
    "fullName": "Intake Manifold Pressure",
    "unit": ""
  },
  "ff1203": {
    "shortName": "kilometers_per_litre_instant",
    "fullName": "Kilometers Per Litre (Instant)",
    "unit": ""
  },
  "ff5202": {
    "shortName": "kilometers_per_litre_long_term_average",
    "fullName": "Kilometers Per Litre (Long Term Average)",
    "unit": ""
  },
  "ff1207": {
    "shortName": "litres_per_100_kilometer_instant",
    "fullName": "Litres Per 100 Kilometer (Instant)",
    "unit": ""
  },
  "ff5203": {
    "shortName": "litres_per_100_kilometer_long_term_average",
    "fullName": "Litres Per 100 Kilometer (Long Term Average)",
    "unit": ""
  },
  "10": {
    "shortName": "mass_air_flow_rate",
    "fullName": "Mass Air Flow Rate",
    "unit": ""
  },
  "ff1201": {
    "shortName": "miles_per_gallon_instant",
    "fullName": "Miles Per Gallon (Instant)",
    "unit": ""
  },
  "ff5201": {
    "shortName": "miles_per_gallon_long_term_average",
    "fullName": "Miles Per Gallon (Long Term Average)",
    "unit": ""
  },
  "24": {
    "shortName": "o2_sensor1_equivalence_ratio",
    "fullName": "O2 Sensor1 Equivalence Ratio",
    "unit": ""
  },
  "34": {
    "shortName": "o2_sensor1_equivalence_ratio_alternate",
    "fullName": "O2 Sensor1 Equivalence Ratio (alternate)",
    "unit": ""
  },
  "ff1240": {
    "shortName": "o2_sensor1_wide_range_voltage",
    "fullName": "O2 Sensor1 wide-range Voltage",
    "unit": ""
  },
  "25": {
    "shortName": "o2_sensor2_equivalence_ratio",
    "fullName": "O2 Sensor2 Equivalence Ratio",
    "unit": ""
  },
  "ff1241": {
    "shortName": "o2_sensor2_wide_range_voltage",
    "fullName": "O2 Sensor2 wide-range Voltage",
    "unit": ""
  },
  "26": {
    "shortName": "o2_sensor3_equivalence_ratio",
    "fullName": "O2 Sensor3 Equivalence Ratio",
    "unit": ""
  },
  "ff1242": {
    "shortName": "o2_sensor3_wide_range_voltage",
    "fullName": "O2 Sensor3 wide-range Voltage",
    "unit": ""
  },
  "27": {
    "shortName": "o2_sensor4_equivalence_ratio",
    "fullName": "O2 Sensor4 Equivalence Ratio",
    "unit": ""
  },
  "ff1243": {
    "shortName": "o2_sensor4_wide_range_voltage",
    "fullName": "O2 Sensor4 wide-range Voltage",
    "unit": ""
  },
  "28": {
    "shortName": "o2_sensor5_equivalence_ratio",
    "fullName": "O2 Sensor5 Equivalence Ratio",
    "unit": ""
  },
  "ff1244": {
    "shortName": "o2_sensor5_wide_range_voltage",
    "fullName": "O2 Sensor5 wide-range Voltage",
    "unit": ""
  },
  "29": {
    "shortName": "o2_sensor6_equivalence_ratio",
    "fullName": "O2 Sensor6 Equivalence Ratio",
    "unit": ""
  },
  "ff1245": {
    "shortName": "o2_sensor6_wide_range_voltage",
    "fullName": "O2 Sensor6 wide-range Voltage",
    "unit": ""
  },
  "2a": {
    "shortName": "o2_sensor7_equivalence_ratio",
    "fullName": "O2 Sensor7 Equivalence Ratio",
    "unit": ""
  },
  "ff1246": {
    "shortName": "o2_sensor7_wide_range_voltage",
    "fullName": "O2 Sensor7 wide-range Voltage",
    "unit": ""
  },
  "2b": {
    "shortName": "o2_sensor8_equivalence_ratio",
    "fullName": "O2 Sensor8 Equivalence Ratio",
    "unit": ""
  },
  "ff1247": {
    "shortName": "o2_sensor8_wide_range_voltage",
    "fullName": "O2 Sensor8 wide-range Voltage",
    "unit": ""
  },
  "ff1214": {
    "shortName": "o2_volts_bank_1_sensor_1",
    "fullName": "O2 Volts Bank 1 sensor 1",
    "unit": ""
  },
  "ff1215": {
    "shortName": "o2_volts_bank_1_sensor_2",
    "fullName": "O2 Volts Bank 1 sensor 2",
    "unit": ""
  },
  "ff1216": {
    "shortName": "o2_volts_bank_1_sensor_3",
    "fullName": "O2 Volts Bank 1 sensor 3",
    "unit": ""
  },
  "ff1217": {
    "shortName": "o2_volts_bank_1_sensor_4",
    "fullName": "O2 Volts Bank 1 sensor 4",
    "unit": ""
  },
  "ff1218": {
    "shortName": "o2_volts_bank_2_sensor_1",
    "fullName": "O2 Volts Bank 2 sensor 1",
    "unit": ""
  },
  "ff1219": {
    "shortName": "o2_volts_bank_2_sensor_2",
    "fullName": "O2 Volts Bank 2 sensor 2",
    "unit": ""
  },
  "ff121a": {
    "shortName": "o2_volts_bank_2_sensor_3",
    "fullName": "O2 Volts Bank 2 sensor 3",
    "unit": ""
  },
  "ff121b": {
    "shortName": "o2_volts_bank_2_sensor_4",
    "fullName": "O2 Volts Bank 2 sensor 4",
    "unit": ""
  },
  "5a": {
    "shortName": "relative_accelerator_pedal_position",
    "fullName": "Relative Accelerator Pedal Position",
    "unit": ""
  },
  "45": {
    "shortName": "relative_throttle_position",
    "fullName": "Relative Throttle Position",
    "unit": ""
  },
  "ff124a": {
    "shortName": "tilt_x",
    "fullName": "Tilt (x)",
    "unit": ""
  },
  "ff124b": {
    "shortName": "tilt_y",
    "fullName": "Tilt (y)",
    "unit": ""
  },
  "ff124c": {
    "shortName": "tilt_z",
    "fullName": "Tilt (z)",
    "unit": ""
  },
  "0e": {
    "shortName": "timing_advance",
    "fullName": "Timing Advance",
    "unit": ""
  },
  "ff1225": {
    "shortName": "torque",
    "fullName": "Torque",
    "unit": ""
  },
  "fe1805": {
    "shortName": "transmission_temperature_method_1",
    "fullName": "Transmission Temperature (Method 1)",
    "unit": ""
  },
  "b4": {
    "shortName": "transmission_temperature_method_2",
    "fullName": "Transmission Temperature (Method 2)",
    "unit": ""
  },
  "ff1206": {
    "shortName": "trip_average_kpl",
    "fullName": "Trip average KPL",
    "unit": ""
  },
  "ff1208": {
    "shortName": "trip_average_litres100_km",
    "fullName": "Trip average Litres/100 KM",
    "unit": ""
  },
  "ff1205": {
    "shortName": "trip_average_mpg",
    "fullName": "Trip average MPG",
    "unit": ""
  },
  "ff1204": {
    "shortName": "trip_distance",
    "fullName": "Trip Distance",
    "unit": ""
  },
  "ff120c": {
    "shortName": "trip_distance_stored_in_vehicle_profile",
    "fullName": "Trip distance (stored in vehicle profile)",
    "unit": ""
  },
  "ff1266": {
    "shortName": "trip_time_since_journey_start",
    "fullName": "Trip Time (Since journey start)",
    "unit": ""
  },
  "ff1268": {
    "shortName": "trip_time_whilst_moving",
    "fullName": "Trip Time (whilst moving)",
    "unit": ""
  },
  "ff1267": {
    "shortName": "trip_time_whilst_stationary",
    "fullName": "Trip time (whilst stationary)",
    "unit": ""
  },
  "ff1202": {
    "shortName": "turbo_boost_&_vacuum_gauge",
    "fullName": "Turbo Boost & Vacuum Gauge",
    "unit": ""
  },
  "42": {
    "shortName": "voltage_control_module",
    "fullName": "Voltage (Control Module)",
    "unit": ""
  },
  "ff1238": {
    "shortName": "voltage_obd_adapter",
    "fullName": "Voltage (OBD Adapter)",
    "unit": ""
  },
  "ff1269": {
    "shortName": "volumetric_efficiency_calculated",
    "fullName": "Volumetric Efficiency (Calculated)",
    "unit": ""
  }
}
