"""Configuration and options flow for Pironman 5."""
import logging
import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import API_PATH, DEFAULT_HOST, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DOMAIN
from .models import AUTO, CONF_MODEL, MODEL_NAMES, resolve_model

_LOGGER = logging.getLogger(__name__)
CONF_SCAN_INTERVAL = "scan_interval"

async def validate_connection(hass, host, port):
    """Validate endpoint before saving settings."""
    host = host.strip()
    if not host or '/' in host or ':' in host or ' ' in host:
        raise ValueError("Invalid hostname or IPv4 address")
    session = async_get_clientsession(hass)
    async with session.get(
        f"http://{host}:{port}{API_PATH}/get-device-info",
        timeout=aiohttp.ClientTimeout(total=5),
    ) as response:
        response.raise_for_status()
        result = await response.json()
    if not isinstance(result, dict) or result.get("status") is not True:
        raise ValueError("Invalid Pironman API response")
    return result.get("data") or {}

class Pironman5ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                info = await validate_connection(self.hass, user_input[CONF_HOST], user_input[CONF_PORT])
                await self.async_set_unique_id(user_input[CONF_HOST].strip())
                self._abort_if_unique_id_configured()
                model, _ = resolve_model(info, user_input.get(CONF_MODEL, AUTO))
                return self.async_create_entry(
                    title=MODEL_NAMES[model] if model else info.get("name", "Pironman 5"),
                    data=user_input,
                )
            except (aiohttp.ClientError, TimeoutError, ValueError) as err:
                _LOGGER.debug("Pironman connection error: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected Pironman configuration error")
                errors["base"] = "unknown"
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
                vol.Required(CONF_MODEL, default=AUTO): vol.In([AUTO, *MODEL_NAMES]),
            }),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return Pironman5OptionsFlow()

class Pironman5OptionsFlow(config_entries.OptionsFlow):

    async def async_step_init(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                await validate_connection(self.hass, user_input[CONF_HOST], user_input[CONF_PORT])
                return self.async_create_entry(title="", data=user_input)
            except (aiohttp.ClientError, TimeoutError, ValueError) as err:
                _LOGGER.debug("Pironman options connection error: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected Pironman options error")
                errors["base"] = "unknown"
        opts = self.config_entry.options
        data = self.config_entry.data
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST, default=opts.get(CONF_HOST, data.get(CONF_HOST, DEFAULT_HOST))): str,
                vol.Required(CONF_PORT, default=opts.get(CONF_PORT, data.get(CONF_PORT, DEFAULT_PORT))): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
                vol.Required(CONF_SCAN_INTERVAL, default=opts.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)): vol.All(vol.Coerce(int), vol.Range(min=5, max=60)),
                vol.Required(CONF_MODEL, default=opts.get(CONF_MODEL, data.get(CONF_MODEL, AUTO))): vol.In([AUTO, *MODEL_NAMES]),
            }),
            errors=errors,
        )
