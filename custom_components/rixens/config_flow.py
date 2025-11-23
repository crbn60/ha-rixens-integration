# custom_components/rixens/config_flow.py

import voluptuous as vol
import aiohttp
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, RIXENS_URL, UPDATE_INTERVAL
from . import RixensApiClient


class RixensConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Rixens."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            base_url = user_input[RIXENS_URL].rstrip("/")  # Clean up trailing slash

            # Use base URL for unique ID
            await self.async_set_unique_id(base_url)
            self._abort_if_unique_id_configured()

            # Test the connection to the device
            try:
                info = await self._test_connection(base_url)
            except aiohttp.ClientConnectorError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"

            if not errors:
                return self.async_create_entry(title=info["name"], data=user_input)

        # Show the form to the user
        data_schema = vol.Schema(
            {
                vol.Required(RIXENS_URL): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def _test_connection(self, base_url):
        """Test the connection and fetch device info."""
        # Use a temporary client initialized with the base URL
        api = RixensApiClient(aiohttp.ClientSession(), base_url)
        data = await api.fetch_data()

        # We assume the version string contains RIXENS, which makes a good unique name
        version_string = data.get("version", "Rixens Device")

        return {"name": version_string.split()[-1]}


@callback
def async_get_options_flow(config_entry):
    """Get the options flow for this handler."""
    return RixensOptionsFlowHandler(config_entry)


class RixensOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for Rixens integration (for future settings)."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options for the integration.

        Currently exposes `update_interval` in seconds.
        """
        errors = {}

        # Current value or default
        current = self.config_entry.options.get("update_interval", UPDATE_INTERVAL)

        if user_input is not None:
            # Save options
            return self.async_create_entry(title="", data=user_input)

            data_schema = vol.Schema(
                {
                    vol.Optional("update_interval", default=int(current)): vol.All(
                        int,
                        vol.Range(min=2, max=3600),
                    ),
                }
            )

        return self.async_show_form(
            step_id="init", data_schema=data_schema, errors=errors
        )
