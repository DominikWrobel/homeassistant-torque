"""Runtime models for Torque Logger."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
import logging
import math
import re
import re
from time import monotonic
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.storage import Store

from .const import (
    CONF_ENDPOINT_ID,
    CONF_VEHICLE_NAME,
    GPS_ACCURACY_KEYS,
    GPS_LAT_KEYS,
    GPS_LON_KEYS,
    MAX_SENSORS_PER_VEHICLE,
    SPECIAL_NAMES,
    SPECIAL_UNITS,
    STORAGE_KEY_PREFIX,
    STORAGE_VERSION,
)

from .pid_definitions import apply_defaults

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class TorquePid:
    """Metadata and value for one Torque PID."""

    pid: str
    value: Any = None
    name: str | None = None
    short_name: str | None = None
    unit: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Serialize PID."""
        return {
            "pid": self.pid,
            "value": self.value,
            "name": self.name,
            "short_name": self.short_name,
            "unit": self.unit,
        }


class TorqueVehicle:
    """One configured vehicle."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.pids: dict[str, TorquePid] = {}
        self.gps_latitude: float | None = None
        self.gps_longitude: float | None = None
        self.gps_accuracy: float | None = None
        self.last_update: datetime | None = None
        self._active_session: str | None = None
        self._last_update_entity_publish = float("-inf")
        self._last_save = float("-inf")
        self._dirty = False
        self._listeners: list[Callable[[str, str | None], None]] = []
        self._store: Store[dict[str, Any]] = Store(
            hass,
            STORAGE_VERSION,
            f"{STORAGE_KEY_PREFIX}.{entry.entry_id}",
        )

    @property
    def vehicle_name(self) -> str:
        """Return configured vehicle name."""
        return str(
            self.entry.options.get(
                CONF_VEHICLE_NAME,
                self.entry.data.get(CONF_VEHICLE_NAME, self.entry.title),
            )
        )

    @property
    def endpoint_id(self) -> str:
        """Return configured endpoint slug."""
        return str(
            self.entry.options.get(
                CONF_ENDPOINT_ID,
                self.entry.data[CONF_ENDPOINT_ID],
            )
        )

    @property
    def device_identifier(self) -> tuple[str, str]:
        """Stable HA device identifier."""
        return ("torque_logger", self.entry.entry_id)

    async def async_load(self) -> None:
        """Restore discovered PIDs and last values."""
        data = await self._store.async_load()
        if not data:
            return

        for raw in data.get("pids", []):
            try:
                pid = str(raw["pid"])
                self.pids[pid] = TorquePid(
                    pid=pid,
                    value=raw.get("value"),
                    name=raw.get("name"),
                    short_name=raw.get("short_name"),
                    unit=raw.get("unit"),
                )
            except (KeyError, TypeError, ValueError):
                continue

        for info in self.pids.values():
            apply_defaults(info)

        self.gps_latitude = _to_float(data.get("gps_latitude"))
        self.gps_longitude = _to_float(data.get("gps_longitude"))
        # beta.1 stored altitude as accuracy; recompute from actual accuracy PID.
        self.gps_accuracy = _first_float({}, GPS_ACCURACY_KEYS, self.pids)

        self._active_session = data.get("active_session")
        raw_last_update = data.get("last_update")
        if isinstance(raw_last_update, str):
            try:
                self.last_update = datetime.fromisoformat(raw_last_update)
            except ValueError:
                self.last_update = None

    async def async_remove_storage(self) -> None:
        """Remove persisted runtime data."""
        await self._store.async_remove()

    def _data_to_store(self) -> dict[str, Any]:
        return {
            "pids": [pid.as_dict() for pid in self.pids.values()],
            "gps_latitude": self.gps_latitude,
            "gps_longitude": self.gps_longitude,
            "gps_accuracy": self.gps_accuracy,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "active_session": self._active_session,
        }

    @callback
    def async_add_listener(
        self, listener: Callable[[str, str | None], None]
    ) -> Callable[[], None]:
        """Register runtime listener."""
        self._listeners.append(listener)

        @callback
        def remove_listener() -> None:
            if listener in self._listeners:
                self._listeners.remove(listener)

        return remove_listener

    @callback
    def _notify(self, event: str, pid: str | None = None) -> None:
        for listener in list(self._listeners):
            listener(event, pid)

    @callback
    def async_process_payload(self, payload: dict[str, Any]) -> int:
        """Process one Torque upload. Returns number of updated PID values."""
        normalized = {str(key).strip().lower(): value for key, value in payload.items() if value is not None}
        before = {pid: (info.value, info.name, info.short_name, info.unit) for pid, info in self.pids.items()}
        old_gps = (self.gps_latitude, self.gps_longitude, self.gps_accuracy)

        # Torque's session identifies a continuous logging run. The original
        # integration kept a separate value set per session; clear live values
        # when Torque starts a new run, while keeping discovered sensor metadata.
        session = _clean_text(normalized.get("session"))
        session_changed = bool(session and self._active_session and session != self._active_session)
        if session:
            self._active_session = session
        if session_changed:
            for info in self.pids.values():
                info.value = None
            self.gps_latitude = self.gps_longitude = self.gps_accuracy = None

        # Apply metadata packets even when Torque sends them separately from values.
        for key, raw in normalized.items():
            for prefix, field in (("userfullname", "name"), ("usershortname", "short_name"), ("defaultunit", "unit")):
                if key.startswith(prefix):
                    pid = _canonical_pid(key[len(prefix):])
                    for existing_pid, info in self.pids.items():
                        if _canonical_pid(existing_pid) == pid:
                            text = _clean_text(raw)
                            if text:
                                setattr(info, field, _normalize_unit(text) if field == "unit" else text)
                    break

        updated = 0
        new_pids: list[str] = []

        # Torque sends values as k<PID>. Metadata usually arrives as
        # userFullName<PID>, userShortName<PID>, defaultUnit<PID>.
        for key, raw_value in normalized.items():
            lower_key = key.lower()
            if not re.fullmatch(r"k[0-9a-f]{1,16}", lower_key):
                continue

            pid = _canonical_pid(key[1:])
            # Reuse an existing legacy one-digit key if this installation has it.
            pid = next((old for old in self.pids if _canonical_pid(old) == pid), pid)

            # Metadata fields are not values.
            if pid.startswith(("userfullname", "usershortname", "defaultunit")):
                continue

            if pid not in self.pids and len(self.pids) >= MAX_SENSORS_PER_VEHICLE:
                _LOGGER.warning(
                    "Ignoring new Torque PID %s for %s: per-vehicle limit (%s) reached",
                    pid,
                    self.vehicle_name,
                    MAX_SENSORS_PER_VEHICLE,
                )
                continue

            full_name = _lookup_pid_metadata(normalized, "userfullname", key[1:])
            short_name = _lookup_pid_metadata(normalized, "usershortname", key[1:])
            unit = _lookup_pid_metadata(normalized, "defaultunit", key[1:])

            value = _clean_value(raw_value)
            if value is None:
                continue

            if pid not in self.pids:
                self.pids[pid] = TorquePid(
                    pid=pid,
                    name=_clean_text(full_name)
                    or _clean_text(short_name)
                    or f"PID {pid.upper()}",
                    short_name=_clean_text(short_name),
                    unit=_normalize_unit(_clean_text(unit)),
                )
                new_pids.append(pid)
            else:
                info = self.pids[pid]
                if full_name:
                    info.name = _clean_text(full_name) or info.name
                if short_name:
                    info.short_name = _clean_text(short_name) or info.short_name
                if unit:
                    info.unit = _normalize_unit(_clean_text(unit)) or info.unit

            apply_defaults(self.pids[pid])
            self.pids[pid].value = value
            updated += 1

        # Torque also sends several GPS values without the "k" prefix.
        for gps_key in (
            "gpslat",
            "gpslon",
            "gpsaccuracy",
            "gpsaltitude",
            "gpsspeed",
            "gpsbearing",
            "gpsheading",
        ):
            raw = _lookup_case_insensitive(normalized, gps_key)
            if raw is None:
                continue

            value = _clean_value(raw)
            if value is None:
                continue

            pid = gps_key
            if pid not in self.pids:
                if len(self.pids) < MAX_SENSORS_PER_VEHICLE:
                    self.pids[pid] = TorquePid(
                        pid=pid,
                        name=SPECIAL_NAMES.get(pid, pid),
                        unit=SPECIAL_UNITS.get(pid),
                    )
                    new_pids.append(pid)
            if pid in self.pids:
                self.pids[pid].value = value
                updated += 1

        self.gps_latitude = _first_float(normalized, GPS_LAT_KEYS, self.pids)
        self.gps_longitude = _first_float(normalized, GPS_LON_KEYS, self.pids)
        self.gps_accuracy = _first_float(normalized, GPS_ACCURACY_KEYS, self.pids)

        after = {pid: (info.value, info.name, info.short_name, info.unit) for pid, info in self.pids.items()}
        changed_pids = {pid for pid, state in after.items() if before.get(pid) != state}
        if not updated and not changed_pids and old_gps == (self.gps_latitude, self.gps_longitude, self.gps_accuracy):
            return 0

        self.last_update = datetime.now(timezone.utc)

        # Publish values immediately. Coalescing these events caused the live
        # stream to skip samples and made speed appear to jump in 5 s steps.
        for pid in new_pids:
            self._notify("new_pid", pid)
        for pid in changed_pids:
            self._notify("updated", pid)
        if old_gps != (self.gps_latitude, self.gps_longitude, self.gps_accuracy):
            self._notify("updated", "__location__")
        # Last-update is diagnostic; publishing it on every Torque packet only
        # creates avoidable Recorder writes, so limit that entity to 30 seconds.
        if monotonic() - self._last_update_entity_publish >= 30:
            self._last_update_entity_publish = monotonic()
            self._notify("updated", "__last_update__")

        self._dirty = True
        if monotonic() - self._last_save >= 60:
            self._last_save = monotonic()
            self._store.async_delay_save(self._data_to_store, 1)
        return updated

    @callback
    def _publish_pending(self) -> None:
        self._publish_handle = None
        for pid in self._pending_new:
            self._notify("new_pid", pid)
        for pid in self._pending_pids:
            self._notify("updated", pid)
        self._pending_new.clear()
        self._pending_pids.clear()

    async def async_shutdown(self) -> None:
        """Cancel delayed publication and flush latest values on clean unload."""
        if self._dirty:
            await self._store.async_save(self._data_to_store())
        self._listeners.clear()



def _canonical_pid(pid: str) -> str:
    """Match the original parser: standard one-digit PIDs are two digits."""
    value = pid.lower()
    if re.fullmatch(r"[0-9a-f]", value):
        return value.zfill(2)
    return value


def _lookup_pid_metadata(data: dict[str, Any], prefix: str, pid: str) -> Any:
    canonical = _canonical_pid(pid)
    for key, value in data.items():
        if key.startswith(prefix) and _canonical_pid(key[len(prefix):]) == canonical:
            return value
    return None

def _lookup_case_insensitive(data: dict[str, Any], wanted: str) -> Any:
    return data.get(wanted.lower())


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _clean_value(value: Any) -> Any | None:
    if value is None:
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            return None
        return value

    text = str(value).strip()
    if not text or text.lower() in {"nan", "inf", "+inf", "-inf", "infinity", "---", "null", "none"}:
        return None

    try:
        number = float(text)
        if not math.isfinite(number):
            return None
        if number.is_integer():
            return int(number)
        return number
    except ValueError:
        return text


def _to_float(value: Any) -> float | None:
    cleaned = _clean_value(value)
    if isinstance(cleaned, (int, float)):
        return float(cleaned)
    return None


def _first_float(
    payload: dict[str, Any],
    keys: tuple[str, ...],
    pids: dict[str, TorquePid],
) -> float | None:
    for key in keys:
        raw = _lookup_case_insensitive(payload, key)
        parsed = _to_float(raw)
        if parsed is not None:
            return parsed

        pid_key = key[1:].lower() if key.lower().startswith("k") else key.lower()
        info = pids.get(pid_key)
        if info is not None:
            parsed = _to_float(info.value)
            if parsed is not None:
                return parsed
    return None


def _normalize_unit(unit: str | None) -> str | None:
    if unit is None:
        return None

    normalized = unit.strip()
    aliases = {
        "degc": "°C",
        "c": "°C",
        "degrees c": "°C",
        "degf": "°F",
        "f": "°F",
        "degrees f": "°F",
        "kmph": "km/h",
        "kph": "km/h",
        "mph": "mph",
        "rpm": "rpm",
        "volts": "V",
        "volt": "V",
        "amps": "A",
        "amp": "A",
        "percent": "%",
        "pct": "%",
        "litres": "L",
        "liters": "L",
        "l/100km": "L/100 km",
        "g/s": "g/s",
        "kg/h": "kg/h",
        "degrees": "°",
        "deg": "°",
    }
    return aliases.get(normalized.lower(), normalized)
