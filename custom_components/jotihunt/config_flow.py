"""Config flow voor Jotihunt."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    MAX_UPDATE_INTERVAL,
    MIN_UPDATE_INTERVAL,
)


class JotihuntConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow: geen credentials nodig, de API is publiek toegankelijk."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        # Slechts één instantie nodig, er is maar één Jotihunt API.
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(title="Jotihunt", data={}, options=user_input)

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL
                ): vol.All(int, vol.Range(min=MIN_UPDATE_INTERVAL, max=MAX_UPDATE_INTERVAL)),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> JotihuntOptionsFlow:
        return JotihuntOptionsFlow(config_entry)


class JotihuntOptionsFlow(config_entries.OptionsFlow):
    """Laat de gebruiker achteraf het update-interval aanpassen."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self._config_entry.options.get(
            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
        )
        schema = vol.Schema(
            {
                vol.Optional(CONF_UPDATE_INTERVAL, default=current): vol.All(
                    int, vol.Range(min=MIN_UPDATE_INTERVAL, max=MAX_UPDATE_INTERVAL)
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
