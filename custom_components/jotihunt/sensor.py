"""Sensor platform voor Jotihunt: één entiteit per area."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import AREA_ICON, DOMAIN
from .coordinator import JotihuntUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Zet de sensor entiteiten op en voeg nieuwe areas dynamisch toe."""
    coordinator: JotihuntUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    known_areas: set[str] = set()

    @callback
    def _add_new_areas() -> None:
        new_areas = set(coordinator.data or {}) - known_areas
        if not new_areas:
            return
        known_areas.update(new_areas)
        async_add_entities(
            JotihuntAreaSensor(coordinator, entry, area_name) for area_name in new_areas
        )

    _add_new_areas()
    entry.async_on_unload(coordinator.async_add_listener(_add_new_areas))


class JotihuntAreaSensor(CoordinatorEntity[JotihuntUpdateCoordinator], SensorEntity):
    """Representeert de status van één Jotihunt area (gebied)."""

    _attr_has_entity_name = True
    _attr_icon = AREA_ICON

    def __init__(
        self, coordinator: JotihuntUpdateCoordinator, entry: ConfigEntry, area_name: str
    ) -> None:
        super().__init__(coordinator)
        self._area_name = area_name
        self._attr_unique_id = f"{entry.entry_id}_{area_name.lower()}"
        self._attr_name = area_name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Jotihunt",
            manufacturer="Jotihunt",
            model="Areas",
            entry_type="service",
        )

    @property
    def _area_data(self) -> dict[str, Any] | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._area_name)

    @property
    def available(self) -> bool:
        return super().available and self._area_data is not None

    @property
    def native_value(self) -> str | None:
        data = self._area_data
        return data["status"] if data else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self._area_data
        if not data:
            return {}
        return {"updated_at": data.get("updated_at")}
