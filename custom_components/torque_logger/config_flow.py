"""Config flow for Torque Logger."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.util import slugify

from .const import CONF_ENDPOINT_ID, CONF_VEHICLE_NAME, DOMAIN


def _endpoint_schema(
    vehicle_name: str = "",
    endpoint_id: str = "",
) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_VEHICLE_NAME,
                default=vehicle_name,
            ): str,
            vol.Optional(
                CONF_ENDPOINT_ID,
                default=endpoint_id,
            ): str,
        }
    )


def _normalize_endpoint(vehicle_name: str, endpoint_id: str) -> str:
    candidate = endpoint_id.strip() or vehicle_name.strip()
    return slugify(candidate)


def _endpoint_is_used(
    flow: config_entries.ConfigFlow,
    endpoint_id: str,
    exclude_entry_id: str | None = None,
) -> bool:
    for entry in flow._async_current_entries():
        if exclude_entry_id and entry.entry_id == exclude_entry_id:
            continue
        current = str(
            entry.options.get(
                CONF_ENDPOINT_ID,
                entry.data.get(CONF_ENDPOINT_ID, ""),
            )
        )
        if current == endpoint_id:
            return True
    return False


class TorqueLoggerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Torque Logger."""

    VERSION = 2

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            vehicle_name = str(user_input[CONF_VEHICLE_NAME]).strip()
            endpoint_id = _normalize_endpoint(
                vehicle_name,
                str(user_input.get(CONF_ENDPOINT_ID, "")),
            )

            if not vehicle_name:
                errors[CONF_VEHICLE_NAME] = "vehicle_name_required"
            elif not endpoint_id:
                errors[CONF_ENDPOINT_ID] = "invalid_endpoint"
            elif _endpoint_is_used(self, endpoint_id):
                errors[CONF_ENDPOINT_ID] = "endpoint_exists"
            else:
                return self.async_create_entry(
                    title=vehicle_name,
                    data={
                        CONF_VEHICLE_NAME: vehicle_name,
                        CONF_ENDPOINT_ID: endpoint_id,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_endpoint_schema(),
            errors=errors,
            description_placeholders={
                "example": "/api/torque_logger/seat_leon",
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> TorqueLoggerOptionsFlow:
        return TorqueLoggerOptionsFlow()


class TorqueLoggerOptionsFlow(config_entries.OptionsFlow):
    """Edit vehicle name and endpoint from the GUI."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}

        current_name = str(
            self.config_entry.options.get(
                CONF_VEHICLE_NAME,
                self.config_entry.data[CONF_VEHICLE_NAME],
            )
        )
        current_endpoint = str(
            self.config_entry.options.get(
                CONF_ENDPOINT_ID,
                self.config_entry.data[CONF_ENDPOINT_ID],
            )
        )

        if user_input is not None:
            vehicle_name = str(user_input[CONF_VEHICLE_NAME]).strip()
            endpoint_id = _normalize_endpoint(
                vehicle_name,
                str(user_input.get(CONF_ENDPOINT_ID, "")),
            )

            if not vehicle_name:
                errors[CONF_VEHICLE_NAME] = "vehicle_name_required"
            elif not endpoint_id:
                errors[CONF_ENDPOINT_ID] = "invalid_endpoint"
            else:
                # OptionsFlow has hass/config_entry; inspect all entries directly.
                for entry in self.hass.config_entries.async_entries(DOMAIN):
                    if entry.entry_id == self.config_entry.entry_id:
                        continue
                    other_endpoint = str(
                        entry.options.get(
                            CONF_ENDPOINT_ID,
                            entry.data.get(CONF_ENDPOINT_ID, ""),
                        )
                    )
                    if other_endpoint == endpoint_id:
                        errors[CONF_ENDPOINT_ID] = "endpoint_exists"
                        break

            if not errors:
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    title=vehicle_name,
                )
                return self.async_create_entry(
                    title="",
                    data={
                        CONF_VEHICLE_NAME: vehicle_name,
                        CONF_ENDPOINT_ID: endpoint_id,
                    },
                )

        return self.async_show_form(
            step_id="init",
            data_schema=_endpoint_schema(current_name, current_endpoint),
            errors=errors,
            description_placeholders={
                "endpoint": f"/api/torque_logger/{current_endpoint}",
            },
        )
