"""Diagnostics for Torque Logger."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DATA_VEHICLES, DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return non-secret diagnostics."""
    vehicle = hass.data[DOMAIN][DATA_VEHICLES][entry.entry_id]

    return {
        "vehicle_name": vehicle.vehicle_name,
        "endpoint": f"/api/torque_logger/{vehicle.endpoint_id}",
        "pid_count": len(vehicle.pids),
        "pids": {
            pid: {
                "name": info.name,
                "short_name": info.short_name,
                "unit": info.unit,
                "has_value": info.value is not None,
            }
            for pid, info in sorted(vehicle.pids.items())
        },
        "gps_available": (
            vehicle.gps_latitude is not None
            and vehicle.gps_longitude is not None
        ),
        "last_update": (
            vehicle.last_update.isoformat()
            if vehicle.last_update
            else None
        ),
    }
