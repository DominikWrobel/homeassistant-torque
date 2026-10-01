"""Torque Logger sensor platform."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify

from .const import DATA_VEHICLES, DOMAIN
from .models import TorquePid, TorqueVehicle


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for one vehicle."""
    vehicle: TorqueVehicle = hass.data[DOMAIN][DATA_VEHICLES][entry.entry_id]

    entities: list[SensorEntity] = [
        TorquePidSensor(vehicle, pid)
        for pid in sorted(vehicle.pids)
    ]
    entities.append(TorqueLastUpdateSensor(vehicle))
    async_add_entities(entities)

    known = set(vehicle.pids)

    @callback
    def handle_vehicle_event(event: str, pid: str | None) -> None:
        if event != "new_pid" or not pid or pid in known:
            return
        known.add(pid)
        async_add_entities([TorquePidSensor(vehicle, pid)])

    entry.async_on_unload(vehicle.async_add_listener(handle_vehicle_event))


class TorqueBaseSensor(SensorEntity):
    """Common Torque sensor base."""

    _attr_has_entity_name = True

    def __init__(self, vehicle: TorqueVehicle) -> None:
        self.vehicle = vehicle

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={vehicle_identifier(self.vehicle)},
            name=self.vehicle.vehicle_name,
            manufacturer="Torque",
            model="OBD-II vehicle",
        )


class TorquePidSensor(TorqueBaseSensor):
    """One dynamically discovered Torque PID."""

    def __init__(self, vehicle: TorqueVehicle, pid: str) -> None:
        super().__init__(vehicle)
        self.pid = pid
        self._attr_unique_id = f"{vehicle.entry.entry_id}_pid_{pid}"
        self._attr_suggested_object_id = (
            f"{vehicle.endpoint_id}_{slugify(self.name_from_pid)}"
        )

    @property
    def info(self) -> TorquePid:
        return self.vehicle.pids[self.pid]

    @property
    def name_from_pid(self) -> str:
        info = self.vehicle.pids.get(self.pid)
        if info:
            return info.name or info.short_name or f"PID {self.pid.upper()}"
        return f"PID {self.pid.upper()}"

    @property
    def name(self) -> str:
        return self.name_from_pid

    @property
    def native_value(self) -> Any:
        return self.info.value

    @property
    def native_unit_of_measurement(self) -> str | None:
        return self.info.unit

    @property
    def state_class(self) -> SensorStateClass | None:
        if isinstance(self.info.value, (int, float)):
            return SensorStateClass.MEASUREMENT
        return None

    @property
    def device_class(self) -> SensorDeviceClass | None:
        return _device_class_for(self.info.name, self.info.unit, self.pid)

    @property
    def icon(self) -> str | None:
        return _icon_for(self.info.name, self.pid)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "pid": self.pid,
            "torque_short_name": self.info.short_name,
            "torque_unit": self.info.unit,
            "vehicle_endpoint": f"/api/torque_logger/{self.vehicle.endpoint_id}",
        }

    async def async_added_to_hass(self) -> None:
        @callback
        def handle_vehicle_event(event: str, pid: str | None) -> None:
            if event == "updated":
                self.async_write_ha_state()

        self.async_on_remove(self.vehicle.async_add_listener(handle_vehicle_event))


class TorqueLastUpdateSensor(TorqueBaseSensor):
    """Timestamp of the latest Torque upload."""

    _attr_name = "Last update"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, vehicle: TorqueVehicle) -> None:
        super().__init__(vehicle)
        self._attr_unique_id = f"{vehicle.entry.entry_id}_last_update"
        self._attr_suggested_object_id = f"{vehicle.endpoint_id}_last_update"

    @property
    def native_value(self) -> datetime | None:
        return self.vehicle.last_update

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "endpoint": f"/api/torque_logger/{self.vehicle.endpoint_id}",
            "discovered_pids": len(self.vehicle.pids),
        }

    async def async_added_to_hass(self) -> None:
        @callback
        def handle_vehicle_event(event: str, pid: str | None) -> None:
            if event == "updated":
                self.async_write_ha_state()

        self.async_on_remove(self.vehicle.async_add_listener(handle_vehicle_event))


def vehicle_identifier(vehicle: TorqueVehicle) -> tuple[str, str]:
    return (DOMAIN, vehicle.entry.entry_id)


def _device_class_for(
    name: str | None,
    unit: str | None,
    pid: str,
) -> SensorDeviceClass | None:
    text = (name or "").lower()
    normalized_unit = (unit or "").strip()

    # Location coordinates must remain plain numeric sensors.
    if pid in {"gpslat", "gpslon"}:
        return None

    if normalized_unit in {"°C", "°F"}:
        return SensorDeviceClass.TEMPERATURE
    if normalized_unit in {"km/h", "mph"}:
        return SensorDeviceClass.SPEED
    if normalized_unit in {"V", "mV"}:
        return SensorDeviceClass.VOLTAGE
    if normalized_unit in {"A", "mA"}:
        return SensorDeviceClass.CURRENT
    if normalized_unit in {"W", "kW"}:
        return SensorDeviceClass.POWER
    if normalized_unit in {"Wh", "kWh"}:
        return SensorDeviceClass.ENERGY
    if normalized_unit in {"Pa", "hPa", "kPa", "bar", "psi"}:
        return SensorDeviceClass.PRESSURE
    if normalized_unit in {"m", "km", "mi", "ft"}:
        if "altitude" not in text and "accuracy" not in text:
            return SensorDeviceClass.DISTANCE

    if "battery" in text and normalized_unit == "%":
        return SensorDeviceClass.BATTERY

    return None


def _icon_for(name: str | None, pid: str) -> str | None:
    text = (name or "").lower()

    if "rpm" in text or "engine speed" in text:
        return "mdi:engine"
    if "fuel" in text:
        return "mdi:gas-station"
    if "speed" in text:
        return "mdi:speedometer"
    if "temperature" in text or "temp" in text:
        return "mdi:thermometer"
    if "voltage" in text or "volt" in text:
        return "mdi:car-battery"
    if "throttle" in text:
        return "mdi:car-cruise-control"
    if "pressure" in text:
        return "mdi:gauge"
    if pid in {"gpslat", "gpslon"} or "gps" in text:
        return "mdi:crosshairs-gps"
    return None
