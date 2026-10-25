"""Constants for the Westnetz MeDaCo integration."""

from datetime import timedelta

DOMAIN = "medaco"

CONF_PORTAL = "portal"

# Both network operators run the same MeDaCo portal software.
PORTALS = {
    "westnetz": "https://medaco.westnetz.de",
    "westenergie": "https://medaco.westenergie.de",
}
DEFAULT_PORTAL = "westnetz"

# Options (Settings → Devices & services → MeDaCo → Configure).
# Import values the portal still marks as provisional (state "v")? Those are
# profile estimates for the current day that get replaced by measured values
# once the gateway has transmitted, usually the next day.
CONF_INCLUDE_PROVISIONAL = "include_provisional"
DEFAULT_INCLUDE_PROVISIONAL = False
# Re-import the last N days on every run so late corrections (substitute
# values, provisional values turning final) end up in the statistics.
CONF_REIMPORT_DAYS = "reimport_days"
DEFAULT_REIMPORT_DAYS = 2
MAX_REIMPORT_DAYS = 30

# Poll interval. The gateway usually transmits once a day, so this mainly
# catches the moment the new day's values appear.
UPDATE_INTERVAL = timedelta(minutes=15)

# How far back to fetch on the very first import, and the size of each
# request while catching up.
INITIAL_HISTORY = timedelta(days=365)
FETCH_CHUNK = timedelta(days=31)

# OBIS codes of the 15 minute energy registers (1.29.0 = Bezug, 2.29.0 =
# Einspeisung) the portal reports for an intelligent metering system.
OBIS_CONSUMPTION = "1-1:1.29.0"
OBIS_FEED_IN = "1-1:2.29.0"
OBIS_NAMES = {
    OBIS_CONSUMPTION: "Bezug",
    OBIS_FEED_IN: "Einspeisung",
}

# Value states the portal reports alongside each interval.
STATE_MEASURED = "W"  # gemessen
STATE_SUBSTITUTE = "E"  # Ersatzwert des Messstellenbetreibers
STATE_PROVISIONAL = "v"  # vorläufig: Schätzung, bis der Zähler übertragen hat
