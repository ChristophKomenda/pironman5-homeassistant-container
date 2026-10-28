from homeassistant.components.select import SelectEntity

from .entity import PironmanEntity
from .oled import PironmanOLED


FAN_MODES = {
    "Always On": 0,
    "Performance": 1,
    "Cool": 2,
    "Balanced": 3,
    "Quiet": 4,
}


GPIO_FAN_LED_MODES = {
    "On": "on",
    "Off": "off",
    "Follow": "follow",
}


RGB_EFFECTS = {
    "Solid": "solid",
    "Breathing": "breathing",
    "Flow": "flow",
    "Flow Reverse": "flow_reverse",
    "Rainbow": "rainbow",
    "Rainbow Reverse": "rainbow_reverse",
    "Hue Cycle": "hue_cycle",
}


OLED_PAGES = {
    "Mix": "mix",
    "Performance": "performance",
    "IPs": "ips",
    "Disk": "disk",
}


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    coordinator = entry.runtime_data

    entities = []

    if coordinator.supports("gpio_fan_mode"):
        entities.append(PironmanFanMode(coordinator, entry.entry_id))

    if coordinator.supports("gpio_fan_led"):
        entities.append(PironmanGPIOFanLED(coordinator, entry.entry_id))

    if coordinator.supports("ws2812"):
        entities.append(PironmanRGBEffect(coordinator, entry.entry_id))

    if coordinator.supports("oled"):
        entities.extend([
            PironmanOLEDRotation(coordinator, entry.entry_id),
            PironmanOLEDPage(coordinator, entry.entry_id),
        ])

    async_add_entities(entities)


class PironmanFanMode(PironmanEntity, SelectEntity):
    _attr_name = "Fan Mode"
    _attr_has_entity_name = True
    _attr_options = list(FAN_MODES.keys())

    def __init__(
        self,
        coordinator,
        entry_id,
    ):
        super().__init__(coordinator)

        self._attr_unique_id = f"{entry_id}_fan_mode"

    @property
    def current_option(self):
        mode = self.coordinator.data.get(
            "gpio_fan_mode"
        )

        reverse = {
            value: key
            for key, value in FAN_MODES.items()
        }

        return reverse.get(mode)

    async def async_select_option(self, option):
        await self.coordinator.post(
            "set-fan-mode",
            {"fan_mode": FAN_MODES[option]},
        )


class PironmanGPIOFanLED(PironmanEntity, SelectEntity):
    _attr_name = "GPIO Fan LED"
    _attr_has_entity_name = True
    _attr_options = list(GPIO_FAN_LED_MODES.keys())
    _attr_icon = "mdi:led-on"

    def __init__(
        self,
        coordinator,
        entry_id,
    ):
        super().__init__(coordinator)

        self._attr_unique_id = f"{entry_id}_gpio_fan_led"

    @property
    def current_option(self):
        led = self.coordinator.data.get(
            "gpio_fan_led"
        )

        reverse = {
            value: key
            for key, value in GPIO_FAN_LED_MODES.items()
        }

        return reverse.get(led)

    async def async_select_option(self, option):
        await self.coordinator.post(
            "set-fan-led",
            {"led": GPIO_FAN_LED_MODES[option]},
        )


class PironmanRGBEffect(PironmanEntity, SelectEntity):
    _attr_name = "RGB Effect"
    _attr_has_entity_name = True
    _attr_options = list(RGB_EFFECTS.keys())
    _attr_icon = "mdi:palette"

    def __init__(
        self,
        coordinator,
        entry_id,
    ):
        super().__init__(coordinator)

        self._attr_unique_id = f"{entry_id}_rgb_effect"

    @property
    def current_option(self):
        style = self.coordinator.data.get(
            "rgb_style"
        )

        reverse = {
            value: key
            for key, value in RGB_EFFECTS.items()
        }

        return reverse.get(style)

    async def async_select_option(self, option):
        await self.coordinator.post(
            "set-rgb-style",
            {"style": RGB_EFFECTS[option]},
        )


class PironmanOLEDRotation(PironmanEntity, SelectEntity):
    _attr_name = "OLED Rotation"
    _attr_has_entity_name = True
    _attr_options = [
        "0°",
        "180°",
    ]
    _attr_icon = "mdi:rotate-3d-variant"

    def __init__(
        self,
        coordinator,
        entry_id,
    ):
        super().__init__(coordinator)

        self.oled = PironmanOLED(coordinator)

        self._attr_unique_id = f"{entry_id}_oled_rotation"

    @property
    def current_option(self):
        rotation = self.coordinator.data.get(
            "oled_rotation",
            0,
        )

        return f"{rotation}°"

    async def async_select_option(self, option):
        rotation = int(
            option.rstrip("°")
        )

        await self.oled.set_rotation(rotation)
        await self.coordinator.async_request_refresh()


class PironmanOLEDPage(PironmanEntity, SelectEntity):
    _attr_name = "OLED Page"
    _attr_has_entity_name = True
    _attr_options = list(OLED_PAGES.keys())
    _attr_icon = "mdi:monitor-dashboard"

    def __init__(
        self,
        coordinator,
        entry_id,
    ):
        super().__init__(coordinator)

        self.oled = PironmanOLED(coordinator)

        self._attr_unique_id = f"{entry_id}_oled_page"

    @property
    def current_option(self):
        pages = self.coordinator.data.get(
            "oled_pages",
            [
                "mix",
                "performance",
                "ips",
                "disk",
            ],
        )

        if not pages:
            return None

        reverse = {
            value: key
            for key, value in OLED_PAGES.items()
        }

        return reverse.get(pages[0])

    async def async_select_option(self, option):
        pages = list(
            self.coordinator.data.get(
                "oled_pages",
                [
                    "mix",
                    "performance",
                    "ips",
                    "disk",
                ],
            )
        )

        if not pages:
            pages = [
                "mix",
                "performance",
                "ips",
                "disk",
            ]

        pages[0] = OLED_PAGES[option]

        await self.oled.set_pages(pages)
        await self.coordinator.async_request_refresh()
