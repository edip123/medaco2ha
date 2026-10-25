"""The Westnetz MeDaCo integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import MedacoClient
from .const import CONF_PORTAL, DEFAULT_PORTAL, PORTALS
from .coordinator import MedacoCoordinator

PLATFORMS = [Platform.SENSOR]

type MedacoConfigEntry = ConfigEntry[MedacoCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: MedacoConfigEntry) -> bool:
    """Set up MeDaCo from a config entry."""
    client = MedacoClient(
        # Own session so portal cookies don't leak into other integrations.
        async_create_clientsession(hass),
        PORTALS[entry.data.get(CONF_PORTAL, DEFAULT_PORTAL)],
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
    )
    coordinator = MedacoCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    return True


async def _async_options_updated(hass: HomeAssistant, entry: MedacoConfigEntry) -> None:
    """Reload the entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: MedacoConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
