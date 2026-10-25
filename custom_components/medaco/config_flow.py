"""Config flow for the Westnetz MeDaCo integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
)

from .api import MedacoAuthError, MedacoClient, MedacoError
from .const import (
    CONF_INCLUDE_PROVISIONAL,
    CONF_PORTAL,
    CONF_REIMPORT_DAYS,
    DEFAULT_INCLUDE_PROVISIONAL,
    DEFAULT_PORTAL,
    DEFAULT_REIMPORT_DAYS,
    DOMAIN,
    MAX_REIMPORT_DAYS,
    PORTALS,
)

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PORTAL, default=DEFAULT_PORTAL): SelectSelector(
            SelectSelectorConfig(options=list(PORTALS), translation_key=CONF_PORTAL)
        ),
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class MedacoConfigFlow(ConfigFlow, domain=DOMAIN):
    """Ask for portal credentials and verify them."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> MedacoOptionsFlow:
        """Return the options flow."""
        return MedacoOptionsFlow()

    async def _validate(self, data: Mapping[str, Any]) -> str | None:
        client = MedacoClient(
            async_create_clientsession(self.hass),
            PORTALS[data.get(CONF_PORTAL, DEFAULT_PORTAL)],
            data[CONF_USERNAME],
            data[CONF_PASSWORD],
        )
        try:
            await client.login()
            await client.get_metering_points()
        except MedacoAuthError:
            return "invalid_auth"
        except MedacoError:
            return "cannot_connect"
        return None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_USERNAME].lower())
            self._abort_if_unique_id_configured()
            if (error := await self._validate(user_input)) is None:
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME], data=user_input
                )
            errors["base"] = error
        return self.async_show_form(
            step_id="user", data_schema=USER_SCHEMA, errors=errors
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        entry = self._get_reauth_entry()
        if user_input is not None:
            data = {**entry.data, **user_input}
            if (error := await self._validate(data)) is None:
                return self.async_update_reload_and_abort(entry, data=data)
            errors["base"] = error
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_PASSWORD): str}),
            errors=errors,
        )


class MedacoOptionsFlow(OptionsFlow):
    """Let the user decide how provisional values and corrections are handled."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            user_input[CONF_REIMPORT_DAYS] = int(user_input[CONF_REIMPORT_DAYS])
            return self.async_create_entry(data=user_input)
        options = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_INCLUDE_PROVISIONAL,
                    default=options.get(
                        CONF_INCLUDE_PROVISIONAL, DEFAULT_INCLUDE_PROVISIONAL
                    ),
                ): bool,
                vol.Required(
                    CONF_REIMPORT_DAYS,
                    default=options.get(CONF_REIMPORT_DAYS, DEFAULT_REIMPORT_DAYS),
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=0, max=MAX_REIMPORT_DAYS, step=1, mode=NumberSelectorMode.BOX
                    )
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
