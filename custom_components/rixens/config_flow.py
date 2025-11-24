"""Config flow for Rixens integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_HOST,
    CONF_POLL_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
    MAX_POLL_INTERVAL,
    MIN_POLL_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class RixensConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Rixens MCS7 Controller."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step where user provides host/IP."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()

            # Validate host is not empty
            if not host:
                errors[CONF_HOST] = "invalid_host"
            else:
                # Set unique ID based on host to prevent duplicates
                await self.async_set_unique_id(host.lower())
                self._abort_if_unique_id_configured()

                _LOGGER.info("Creating config entry for Rixens MCS7 at %s", host)
                return self.async_create_entry(
                    title=f"Rixens MCS7 ({host})",
                    data={CONF_HOST: host},
                    options={CONF_POLL_INTERVAL: DEFAULT_POLL_INTERVAL},
                )

        # Use typed schema with selector for better UI
        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_import(self, import_config: dict[str, Any]) -> FlowResult:
        """Handle import from YAML (not supported)."""
        _LOGGER.warning("YAML configuration is not supported for Rixens integration")
        return self.async_abort(reason="import_not_supported")

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return RixensOptionsFlow(config_entry)


class RixensOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Rixens integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options for polling interval."""
        errors: dict[str, str] = {}

        if user_input is not None:
            poll_interval = user_input[CONF_POLL_INTERVAL]

            # Validate poll interval range
            if poll_interval < MIN_POLL_INTERVAL or poll_interval > MAX_POLL_INTERVAL:
                errors[CONF_POLL_INTERVAL] = "interval_out_of_range"
                _LOGGER.warning(
                    "Invalid poll interval %s (must be %s-%s)",
                    poll_interval,
                    MIN_POLL_INTERVAL,
                    MAX_POLL_INTERVAL,
                )
            else:
                _LOGGER.info(
                    "Updating poll interval to %s seconds for %s",
                    poll_interval,
                    self.config_entry.title,
                )
                return self.async_create_entry(
                    title="",
                    data={CONF_POLL_INTERVAL: poll_interval},
                )

        # Use number selector with proper min/max for better UI
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_POLL_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL
                    ),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=MIN_POLL_INTERVAL,
                        max=MAX_POLL_INTERVAL,
                        mode=selector.NumberSelectorMode.BOX,
                        unit_of_measurement="seconds",
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )
