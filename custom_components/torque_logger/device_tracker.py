"""Torque Logger GPS device tracker."""

from __future__ import annotations

from typing import Any

from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.components.device_tracker.const import SourceType
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DATA_VEHICLES, DOMAIN
from .models import TorqueVehicle


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up vehicle GPS tracker."""
    vehicle: TorqueVehicle = hass.data[DOMAIN][DATA_VEHICLES][entry.entry_id]
    async_add_entities([TorqueGpsTracker(vehicle)])


class TorqueGpsTracker(TrackerEntity):
    """GPS tracker for one configured vehicle."""

    _attr_has_entity_name = True
    _attr_name = "Location"

    def __init__(self, vehicle: TorqueVehicle) -> None:
        self.vehicle = vehicle
        self._attr_unique_id = f"{vehicle.entry.entry_id}_location"
        self._attr_suggested_object_id = f"{vehicle.endpoint_id}_location"

    @property
    def source_type(self) -> SourceType:
        return SourceType.GPS

    @property
    def latitude(self) -> float | None:
        return self.vehicle.gps_latitude

    @property
    def longitude(self) -> float | None:
        return self.vehicle.gps_longitude

    @property
    def location_accuracy(self) -> int:
        if self.vehicle.gps_accuracy is None:
            return 0
        return max(0, int(round(self.vehicle.gps_accuracy)))

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.vehicle.entry.entry_id)},
            name=self.vehicle.vehicle_name,
            manufacturer="Torque",
            model="OBD-II vehicle",
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "endpoint": f"/api/torque_logger/{self.vehicle.endpoint_id}",
        }

    async def async_added_to_hass(self) -> None:
        @callback
        def handle_vehicle_event(event: str, pid: str | None) -> None:
            if event == "updated":
                self.async_write_ha_state()

        self.async_on_remove(self.vehicle.async_add_listener(handle_vehicle_event))
