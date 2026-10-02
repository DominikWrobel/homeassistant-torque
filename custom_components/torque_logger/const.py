"""Constants for Torque Logger."""

from __future__ import annotations

DOMAIN = "torque_logger"
PLATFORMS = ["sensor", "device_tracker"]

CONF_VEHICLE_NAME = "vehicle_name"
CONF_ENDPOINT_ID = "endpoint_id"

DEFAULT_VEHICLE_NAME = "Vehicle"

API_BASE = "/api/torque_logger"
API_VEHICLE = "/api/torque_logger/{vehicle_id}"

DATA_VEHICLES = "vehicles"
DATA_ENDPOINTS = "endpoints"
DATA_API_REGISTERED = "api_registered"

STORAGE_VERSION = 1
STORAGE_KEY_PREFIX = "torque_logger"

MAX_SENSORS_PER_VEHICLE = 512

GPS_LAT_KEYS = ("gpslat", "kff1006")
GPS_LON_KEYS = ("gpslon", "kff1005")
GPS_ACCURACY_KEYS = ("gpsaccuracy", "kff1239")
GPS_ALTITUDE_KEYS = ("gpsaltitude", "kff1010")
GPS_SPEED_KEYS = ("gpsspeed", "kff1001")
GPS_BEARING_KEYS = ("gpsbearing", "gpsheading", "kff1007")

SPECIAL_NAMES = {
    "gpslat": "GPS latitude",
    "gpslon": "GPS longitude",
    "gpsaccuracy": "GPS accuracy",
    "gpsaltitude": "GPS altitude",
    "gpsspeed": "GPS speed",
    "gpsbearing": "GPS bearing",
    "gpsheading": "GPS heading",
}

SPECIAL_UNITS = {
    "gpsaccuracy": "m",
    "gpsaltitude": "m",
    "gpsspeed": "km/h",
    "gpsbearing": "°",
    "gpsheading": "°",
}
