"""DataUpdateCoordinator voor Jotihunt."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import async_timeout
from aiohttp import ClientError, ClientResponseError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    API_URL,
    BACKOFF_MULTIPLIER,
    DOMAIN,
    INITIAL_BACKOFF_SECONDS,
    MAX_BACKOFF_SECONDS,
    MAX_CONSECUTIVE_429,
)

_LOGGER = logging.getLogger(__name__)


class JotihuntUpdateCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Haalt alle areas in één API-call op en bewaakt de rate limit."""

    def __init__(self, hass: HomeAssistant, update_interval_seconds: int) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval_seconds),
        )
        self._session = async_get_clientsession(hass)
        self._consecutive_429 = 0
        self._cooldown_until: float | None = None

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        now = dt_util.utcnow().timestamp()
        if self._cooldown_until and now < self._cooldown_until:
            remaining = int(self._cooldown_until - now)
            _LOGGER.debug(
                "Jotihunt: nog in cooldown na 429, %s seconden te gaan; update overgeslagen",
                remaining,
            )
            if self.data is not None:
                return self.data
            raise UpdateFailed(
                f"Nog in cooldown na een 429, probeer over {remaining} seconden opnieuw"
            )

        try:
            async with async_timeout.timeout(15):
                async with self._session.get(API_URL) as response:
                    if response.status == 429:
                        self._handle_rate_limited(response)
                        if self.data is not None:
                            # Geef oude data terug in plaats van te falen, zodat
                            # entiteiten niet direct 'unavailable' worden.
                            return self.data
                        raise UpdateFailed(
                            "Jotihunt API gaf een 429 (rate limit) en er is nog geen data"
                        )
                    response.raise_for_status()
                    payload = await response.json()
        except (ClientError, ClientResponseError) as err:
            raise UpdateFailed(f"Fout bij ophalen Jotihunt data: {err}") from err
        except TimeoutError as err:
            raise UpdateFailed("Timeout bij ophalen Jotihunt data") from err

        # Succesvolle call: reset rate-limit state.
        self._consecutive_429 = 0
        self._cooldown_until = None

        areas = payload.get("data", [])
        return {area["name"]: area for area in areas if "name" in area}

    def _handle_rate_limited(self, response) -> None:
        """Bouw een cooldown-periode op na een 429, met exponentiële backoff."""
        self._consecutive_429 += 1

        retry_after = response.headers.get("Retry-After")
        if retry_after is not None:
            try:
                backoff = int(retry_after)
            except ValueError:
                backoff = INITIAL_BACKOFF_SECONDS
        else:
            backoff = min(
                INITIAL_BACKOFF_SECONDS * (BACKOFF_MULTIPLIER ** (self._consecutive_429 - 1)),
                MAX_BACKOFF_SECONDS,
            )

        if self._consecutive_429 >= MAX_CONSECUTIVE_429:
            backoff = MAX_BACKOFF_SECONDS
            _LOGGER.warning(
                "Jotihunt: %s keer achter elkaar een 429 ontvangen. "
                "We nemen aan dat we (bijna) volledig geblokkeerd zijn en "
                "koelen %s seconden af voordat we het opnieuw proberen.",
                self._consecutive_429,
                backoff,
            )
        else:
            _LOGGER.warning(
                "Jotihunt API gaf een 429 (rate limit); we wachten %s seconden voordat "
                "we het opnieuw proberen.",
                backoff,
            )

        self._cooldown_until = dt_util.utcnow().timestamp() + backoff
