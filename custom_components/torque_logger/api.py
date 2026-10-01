"""HTTP API for Torque Logger."""

from __future__ import annotations

import logging
from typing import Any

from aiohttp import web

from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant
from homeassistant.util import slugify

from .const import (
    API_BASE,
    API_VEHICLE,
    CONF_ENDPOINT_ID,
    DATA_ENDPOINTS,
    DATA_VEHICLES,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


def register_http_views(hass: HomeAssistant) -> None:
    """Register Torque HTTP endpoints once."""
    hass.http.register_view(TorqueVehicleView)
    hass.http.register_view(TorqueLegacyView)


async def _request_payload(request: web.Request) -> dict[str, Any]:
    """Merge query-string and POST body fields."""
    payload: dict[str, Any] = dict(request.query)

    if request.method != "POST":
        return payload

    content_type = (request.content_type or "").lower()

    try:
        if content_type == "application/json":
            body = await request.json()
            if isinstance(body, dict):
                payload.update(body)
        else:
            form = await request.post()
            payload.update(dict(form))
    except Exception as err:  # malformed upload should not crash HA
        _LOGGER.debug("Could not parse Torque POST body: %s", err)

    return payload


def _vehicle_by_endpoint(hass: HomeAssistant, vehicle_id: str):
    domain_data = hass.data.get(DOMAIN, {})
    endpoint_map = domain_data.get(DATA_ENDPOINTS, {})
    entry_id = endpoint_map.get(slugify(vehicle_id))
    if not entry_id:
        return None
    return domain_data.get(DATA_VEHICLES, {}).get(entry_id)


def _vehicle_for_legacy(hass: HomeAssistant, payload: dict[str, Any]):
    """Resolve legacy /api/torque_logger upload."""
    domain_data = hass.data.get(DOMAIN, {})
    vehicles = list(domain_data.get(DATA_VEHICLES, {}).values())

    if not vehicles:
        return None

    if len(vehicles) == 1:
        return vehicles[0]

    profile_name = str(payload.get("profileName", "")).strip()
    if profile_name:
        profile_slug = slugify(profile_name)
        for vehicle in vehicles:
            if profile_slug in {
                slugify(vehicle.vehicle_name),
                slugify(vehicle.endpoint_id),
            }:
                return vehicle

    # Optional legacy email matching if an older entry happens to contain it.
    email = str(payload.get("eml", "")).strip().lower()
    if email:
        for vehicle in vehicles:
            configured = str(vehicle.entry.data.get("email", "")).strip().lower()
            if configured and configured == email:
                return vehicle

    return None


async def _handle_vehicle_upload(
    request: web.Request,
    vehicle,
) -> web.Response:
    payload = await _request_payload(request)

    if not payload:
        return web.Response(status=400, text="No Torque data received")

    updated = vehicle.async_process_payload(payload)
    _LOGGER.debug(
        "Torque upload for %s: %s values updated",
        vehicle.vehicle_name,
        updated,
    )
    return web.Response(text="OK")


class TorqueVehicleView(HomeAssistantView):
    """Vehicle-specific Torque endpoint."""

    url = API_VEHICLE
    name = "api:torque_logger:vehicle"
    requires_auth = True

    async def get(self, request: web.Request, vehicle_id: str) -> web.Response:
        vehicle = _vehicle_by_endpoint(request.app["hass"], vehicle_id)
        if vehicle is None:
            return web.Response(status=404, text="Unknown Torque vehicle")
        return await _handle_vehicle_upload(request, vehicle)

    async def post(self, request: web.Request, vehicle_id: str) -> web.Response:
        vehicle = _vehicle_by_endpoint(request.app["hass"], vehicle_id)
        if vehicle is None:
            return web.Response(status=404, text="Unknown Torque vehicle")
        return await _handle_vehicle_upload(request, vehicle)


class TorqueLegacyView(HomeAssistantView):
    """Backward-compatible /api/torque_logger endpoint."""

    url = API_BASE
    name = "api:torque_logger:legacy"
    requires_auth = True

    async def get(self, request: web.Request) -> web.Response:
        payload = await _request_payload(request)
        vehicle = _vehicle_for_legacy(request.app["hass"], payload)
        if vehicle is None:
            return web.Response(
                status=409,
                text=(
                    "Multiple Torque vehicles are configured. "
                    "Use /api/torque_logger/<vehicle_id>."
                ),
            )
        if not payload:
            return web.Response(status=400, text="No Torque data received")
        vehicle.async_process_payload(payload)
        return web.Response(text="OK")

    async def post(self, request: web.Request) -> web.Response:
        payload = await _request_payload(request)
        vehicle = _vehicle_for_legacy(request.app["hass"], payload)
        if vehicle is None:
            return web.Response(
                status=409,
                text=(
                    "Multiple Torque vehicles are configured. "
                    "Use /api/torque_logger/<vehicle_id>."
                ),
            )
        if not payload:
            return web.Response(status=400, text="No Torque data received")
        vehicle.async_process_payload(payload)
        return web.Response(text="OK")
