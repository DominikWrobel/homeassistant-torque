"""Torque Logger API Client/DataView."""
from typing import TYPE_CHECKING
import logging
import pint
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import callback
from homeassistant.util import slugify

# Add these imports to handle potential NumPy issues
import numpy as np

np.cumproduct = np.cumprod  # Patch the deprecated function

from .const import TORQUE_CODES

if TYPE_CHECKING:
    from .coordinator import TorqueLoggerCoordinator

TIMEOUT = 10
_LOGGER: logging.Logger = logging.getLogger(__package__)

ureg = pint.UnitRegistry()

imperalUnits = {"km": "mi", "°C": "°F", "km/h": "mph", "m": "ft"}

prettyPint = {
    "degC": "°C",
    "degF": "°F",
    "mile / hour": "mph",
    "kilometer / hour": "km/h",
    "mile": "mi",
    "kilometer": "km",
    "meter": "m",
    "foot": "ft",
}


class TorqueReceiveDataView(HomeAssistantView):
    """Handle data from Torque requests."""

    url = "/api/torque_logger"
    name = "api:torque_logger"
    coordinator: 'TorqueLoggerCoordinator'

    def __init__(self, data: dict, email: str, imperial: bool):
        """Initialize a Torque view."""
        self.data = data
        self.email = email
        self.imperial = imperial
        # Add a unique URL suffix based on email to separate instances
        self.url = f"/api/torque_logger/{slugify(email)}"

    @callback
    async def get(self, request):
        """Handle Torque data GET request."""
        _LOGGER.debug(request.query)
        session = self.parse_fields(request.query)
        if session is not None:
            await self._async_publish_data(session)
        return "OK!"

    def parse_fields(self, qdata):  # noqa
        """Handle Torque data request."""
        session: str = qdata.get("session")
        if session is None:
            raise Exception("No Session")

        # Create a unique session ID that includes the email
        unique_session = f"{self.email}_{session}"

        if unique_session not in self.data:
            self.data[unique_session] = {
                "profile": {},
                "unit": {},
                "defaultUnit": {},
                "fullName": {},
                "shortName": {},
                "value": {},
                "unknown": [],
                "time": 0,
            }

        for key, value in qdata.items():
            if key.startswith("userUnit"):
                continue
            if key.startswith("userShortName"):
                item = key[13:]
                self.data[unique_session]["shortName"][item] = value
                continue
            if key.startswith("userFullName"):
                item = key[12:]
                self.data[unique_session]["fullName"][item] = value
                continue
            if key.startswith("defaultUnit"):
                item = key[11:]
                self.data[unique_session]["defaultUnit"][item] = value
                continue
            if key.startswith("k"):
                item = key[1:]
                if len(item) == 1:
                    item = "0" + item
                self.data[unique_session]["value"][item] = value
                continue
            if key.startswith("profile"):
                item = key[7:]
                self.data[unique_session]["profile"][item] = value
                continue
            if key == "eml":
                self.data[unique_session]["profile"]["email"] = value
                continue
            if key == "time":
                self.data[unique_session]["time"] = value
                continue
            if key == "v":
                self.data[unique_session]["profile"]["version"] = value
                continue
            if key == "session":
                continue
            if key == "id":
                self.data[unique_session]["profile"]["id"] = value
                continue

            self.data[unique_session]["unknown"].append({"key": key, "value": value})

        if (self.data[unique_session]["profile"]["email"] == self.email and 
            self.data[unique_session]["profile"]["email"] != ""):
            return unique_session
        raise Exception("Not configured email")

    def _get_field(self, session: str, key: str):
        # Rest of the method remains the same
        ...

    def _get_profile(self, session: str):
        return self.data[session]["profile"]

    def _get_data(self, session: str):
        retdata = {}
        retdata["profile"] = self._get_profile(session)
        retdata["time"] = self.data[session]["time"]
        meta = {}

        for key, _ in self.data[session]["value"].items():
            row_data = self._get_field(session, key)
            if row_data is None:
                continue

            retdata[row_data["short_name"]] = row_data["value"]
            meta[row_data["short_name"]] = {
                "name": row_data["name"],
                "unit": row_data["unit"],
            }

        retdata["meta"] = meta
        # Add the instance identifier to the data
        retdata["instance_id"] = self.email

        return retdata

    async def _async_publish_data(self, session: str):
        session_data = self._get_data(session)
        if "Name" not in session_data["profile"]:
            current_id = session_data["profile"]["id"]
            # Only look for sessions with the same email
            other_sessions = [
                self.data[key]
                for key in self.data.keys()
                if (self.data[key]["profile"]["id"] == current_id and 
                    key.startswith(self.email) and 
                    "Name" in self.data[key]["profile"])
            ]
            if len(other_sessions) == 0:
                _LOGGER.error("Missing profile name from torque data.")
                return
            else:
                session_data["profile"]["Name"] = other_sessions[0]["profile"]["Name"]

        if (self.coordinator is None or self.coordinator.async_set_updated_data is None):
            raise Exception("Invalid coordinator state")

        self.coordinator.async_set_updated_data(session_data)
        await self.coordinator.add_entities(session_data)


def _pretty_units(unit):
    if unit in prettyPint:
        return prettyPint[unit]

    return unit


def _unpretty_units(unit):
    for pint_unit, pretty_unit in prettyPint.items():
        if pretty_unit == unit:
            return pint_unit

    return unit


def _convert_units(value, u_in, u_out):
    q_in = ureg.Quantity(value, u_in)
    q_out = q_in.to(u_out)
    return {"value": round(q_out.magnitude, 2), "unit": str(q_out.units)}


def _pretty_convert_units(value, u_in, u_out):
    p_in = _unpretty_units(u_in)
    p_out = _unpretty_units(u_out)
    res = _convert_units(value, p_in, p_out)
    return {"value": res["value"], "unit": _pretty_units(res["unit"])}
