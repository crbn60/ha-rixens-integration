"""Config flow for Rixens integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_HOST,
    CONF_POLL_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
    MAX_POLL_INTERVAL,
    MIN_POLL_INTERVAL,
)


class RixensConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"Rixens MCS7 ({host})",
                data={CONF_HOST: host},
                options={CONF_POLL_INTERVAL: DEFAULT_POLL_INTERVAL},
            )
        schema = vol.Schema({vol.Required(CONF_HOST): str})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_import(self, import_config: dict) -> FlowResult:
        return self.async_abort(reason="import_not_supported")

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return RixensOptionsFlow(config_entry)


class RixensOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.entry = entry

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        if user_input is not None:
            poll = user_input[CONF_POLL_INTERVAL]
            if poll < MIN_POLL_INTERVAL or poll > MAX_POLL_INTERVAL:
                return self.async_show_form(
                    step_id="init",
                    errors={CONF_POLL_INTERVAL: "interval_out_of_range"},
                    data_schema=self._schema(),
                )
            return self.async_create_entry(title="", data={CONF_POLL_INTERVAL: poll})
        return self.async_show_form(step_id="init", data_schema=self._schema())

    def _schema(self):
        return vol.Schema(
            {
                vol.Required(
                    CONF_POLL_INTERVAL,
                    default=self.entry.options.get(
                        CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL
                    ),
                ): vol.Coerce(int),
            }
        )
