"""Config flow for Rixens integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import RixensApi, RixensConnectionError
from .const import (
    CONF_ADAPTIVE_ACTIVE,
    CONF_ADAPTIVE_IDLE,
    CONF_ADAPTIVE_OFF,
    CONF_BURST_MODE,
    CONF_PORT,
    CONF_POLLING_MODE,
    CONF_SCAN_INTERVAL,
    DEFAULT_ADAPTIVE_ACTIVE,
    DEFAULT_ADAPTIVE_IDLE,
    DEFAULT_ADAPTIVE_OFF,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    POLLING_MODE_ADAPTIVE,
    POLLING_MODE_FIXED,
    SCAN_INTERVAL_MAX,
    SCAN_INTERVAL_MIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    api = RixensApi(
        host=data[CONF_HOST],
        port=data.get(CONF_PORT, DEFAULT_PORT),
        session=async_get_clientsession(hass),
    )

    try:
        status = await api.get_status()
    except RixensConnectionError as err:
        raise CannotConnect from err

    # Return info that you want to store in the config entry
    return {"title": f"Rixens ({data[CONF_HOST]})", "version": status.version}


class RixensConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Rixens."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return RixensOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Check if already configured
            self._async_abort_entries_match({CONF_HOST: user_input[CONF_HOST]})

            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class RixensOptionsFlowHandler(OptionsFlow):
    """Handle options flow for Rixens integration."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage preset temperature and polling options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Get current values from options or use defaults
        current_options = self.config_entry.options
        polling_mode = current_options.get(CONF_POLLING_MODE, POLLING_MODE_FIXED)

        # Build base schema with preset temps
        schema_dict = {
            vol.Optional(
                "preset_away_temp",
                default=current_options.get("preset_away_temp", 10.0),
            ): vol.All(vol.Coerce(float), vol.Range(min=5.0, max=30.0)),
            vol.Optional(
                "preset_home_temp",
                default=current_options.get("preset_home_temp", 20.0),
            ): vol.All(vol.Coerce(float), vol.Range(min=5.0, max=30.0)),
            vol.Optional(
                "preset_sleep_temp",
                default=current_options.get("preset_sleep_temp", 18.0),
            ): vol.All(vol.Coerce(float), vol.Range(min=5.0, max=30.0)),
            vol.Required(
                CONF_POLLING_MODE,
                default=polling_mode,
            ): vol.In([POLLING_MODE_FIXED, POLLING_MODE_ADAPTIVE]),
        }

        # Add polling-mode specific options
        if polling_mode == POLLING_MODE_FIXED:
            schema_dict[
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=current_options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                )
            ] = vol.All(vol.Coerce(int), vol.Range(min=SCAN_INTERVAL_MIN, max=SCAN_INTERVAL_MAX))
        else:  # POLLING_MODE_ADAPTIVE
            schema_dict.update(
                {
                    vol.Required(
                        CONF_ADAPTIVE_ACTIVE,
                        default=current_options.get(CONF_ADAPTIVE_ACTIVE, DEFAULT_ADAPTIVE_ACTIVE),
                    ): vol.All(vol.Coerce(int), vol.Range(min=SCAN_INTERVAL_MIN, max=SCAN_INTERVAL_MAX)),
                    vol.Required(
                        CONF_ADAPTIVE_IDLE,
                        default=current_options.get(CONF_ADAPTIVE_IDLE, DEFAULT_ADAPTIVE_IDLE),
                    ): vol.All(vol.Coerce(int), vol.Range(min=SCAN_INTERVAL_MIN, max=SCAN_INTERVAL_MAX)),
                    vol.Required(
                        CONF_ADAPTIVE_OFF,
                        default=current_options.get(CONF_ADAPTIVE_OFF, DEFAULT_ADAPTIVE_OFF),
                    ): vol.All(vol.Coerce(int), vol.Range(min=SCAN_INTERVAL_MIN, max=SCAN_INTERVAL_MAX)),
                }
            )

        # Add burst mode option
        schema_dict[
            vol.Optional(
                CONF_BURST_MODE,
                default=current_options.get(CONF_BURST_MODE, True),
            )
        ] = bool

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema_dict),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
