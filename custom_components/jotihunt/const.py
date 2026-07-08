"""Constanten voor de Jotihunt integratie."""

DOMAIN = "jotihunt"
API_URL = "https://jotihunt.nl/api/2.0/areas"

CONF_UPDATE_INTERVAL = "update_interval"

# De Jotihunt API staat 30 calls/minuut toe. Eén coordinator-update haalt
# alle areas in 1 API-call op, dus zelfs de ondergrens hieronder blijft
# ruim onder de limiet.
DEFAULT_UPDATE_INTERVAL = 60  # seconden
MIN_UPDATE_INTERVAL = 30  # seconden, harde ondergrens om misbruik te voorkomen
MAX_UPDATE_INTERVAL = 3600  # seconden

# Backoff-instellingen voor het geval de API toch een 429 teruggeeft.
INITIAL_BACKOFF_SECONDS = 60
MAX_BACKOFF_SECONDS = 900  # 15 minuten
BACKOFF_MULTIPLIER = 2
# Aantal opeenvolgende 429's voordat we aannemen dat we volledig geblokkeerd
# zijn en de coordinator flink laten afkoelen.
MAX_CONSECUTIVE_429 = 3

AREA_STATUS_ICONS = {
    "green": "mdi:map-marker-check",
    "orange": "mdi:map-marker-alert",
    "red": "mdi:map-marker-remove",
}
DEFAULT_ICON = "mdi:map-marker-question"
