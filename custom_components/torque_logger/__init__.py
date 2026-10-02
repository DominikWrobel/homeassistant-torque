"""Torque Logger integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import register_http_views
from .const import (
    DATA_API_REGISTERED,
    DATA_ENDPOINTS,
    DATA_VEHICLES,
    DOMAIN,
    PLATFORMS,
)
from .models import TorqueVehicle

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up Torque Logger."""
    domain_data = hass.data.setdefault(
        DOMAIN,
        {
            DATA_VEHICLES: {},
            DATA_ENDPOINTS: {},
            DATA_API_REGISTERED: False,
        },
    )

    if not domain_data[DATA_API_REGISTERED]:
        register_http_views(hass)
        domain_data[DATA_API_REGISTERED] = True

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up one vehicle."""
    domain_data = hass.data.setdefault(
        DOMAIN,
        {
            DATA_VEHICLES: {},
            DATA_ENDPOINTS: {},
            DATA_API_REGISTERED: False,
        },
    )

    if not domain_data[DATA_API_REGISTERED]:
        register_http_views(hass)
        domain_data[DATA_API_REGISTERED] = True

    vehicle = TorqueVehicle(hass, entry)
    await vehicle.async_load()

    domain_data[DATA_VEHICLES][entry.entry_id] = vehicle
    domain_data[DATA_ENDPOINTS][vehicle.endpoint_id] = entry.entry_id

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_entry_updated))
    return True


async def _async_entry_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entry after options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload one vehicle."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unloaded:
        return False

    domain_data = hass.data.get(DOMAIN, {})
    vehicle = domain_data.get(DATA_VEHICLES, {}).pop(entry.entry_id, None)
    if vehicle is not None:
        await vehicle.async_shutdown()
        domain_data.get(DATA_ENDPOINTS, {}).pop(vehicle.endpoint_id, None)

    return True


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove persistent data after deleting a vehicle entry."""
    vehicle = TorqueVehicle(hass, entry)
    await vehicle.async_remove_storage()
