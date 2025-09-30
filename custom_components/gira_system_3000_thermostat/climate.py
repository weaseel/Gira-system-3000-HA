
from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature
from homeassistant.const import UnitOfTemperature
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.components.bluetooth import async_register_callback, BluetoothChange
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from . import DOMAIN, MANUFACTURER_ID, TARGET_TEMPERATURE_PREFIX, CURRENT_TEMPERATURE_PREFIX, TEMPERATURE_LENGTH_BYTES
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    data = hass.data[DOMAIN][entry.entry_id]
    entity = GiraThermostat(data["device_name"], data["device_address"])
    data["entity"] = entity  # store reference for BLE callback
    async_add_entities([entity])


import logging


_LOGGER = logging.getLogger(__name__)


HVAC_MODE_HEAT = "heat"
HVAC_MODE_OFF = "off"


class GiraThermostat(ClimateEntity):
    def __init__(self, device_name, device_address) -> None:
        self._device_name = device_name
        self._device_address = device_address
        self._hvac_mode = HVAC_MODE_OFF
        self._target_temperature = None  # default set temp
        self._current_temperature = None  # default measured temp
        self.client = None


    @property
    def unique_id(self):
        return self._device_address


    @property
    def name(self):
        return self._device_name


    @property
    def address(self):
        return self._device_address


    @property
    def supported_features(self):
        return ClimateEntityFeature.TARGET_TEMPERATURE


    @property
    def temperature_unit(self):
        return UnitOfTemperature.CELSIUS


    @property
    def hvac_modes(self):
        #return [HVAC_MODE_HEAT, HVAC_MODE_OFF]
        return [HVAC_MODE_OFF]


    @property
    def hvac_mode(self):
        return self._hvac_mode


    @property
    def current_temperature(self):
        return self._current_temperature


    @property
    def target_temperature(self):
        return self._target_temperature


    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_address)},
            "name": self._device_name,
            "manufacturer": "Gira",
            "model": "System 3000 Thermostat",
        }


    async def async_set_temperature(self, **kwargs):
        """Handle target temperature change from UI."""
        new_temp = kwargs.get(ATTR_TEMPERATURE)
        if new_temp is not None:
            self._target_temperature = new_temp
            # Todo: Set temperature via BLE
            # This is only a placeholder at the moment
            if self.client == None and False:
                from bleak import BleakClient, BleakError, BLEDevice
                from bleak_retry_connector import establish_connection
                from homeassistant.components import bluetooth

                device = bluetooth.async_ble_device_from_address(self.hass, self.address)

                #client = BleakClient(self.address)
                self.client = await establish_connection(
                    BleakClient,
                    device,
                    self.name,
                    timeout=10,
                    max_attempts=3
                )

                if self.client.is_connected:
                    # Read/write GATT characteristics here
                    services = await self.client.get_services()
                    for service in services:
                        print(f"Service: {service.uuid}")

            _LOGGER.debug(f"Target temperature set to {new_temp}°C for {self._device_name}")
            self.async_write_ha_state()


    async def async_set_hvac_mode(self, hvac_mode):
        """Handle mode change from UI."""
        if hvac_mode in self.hvac_modes:
            self._hvac_mode = hvac_mode
            # Todo enable or disable heating
            _LOGGER.debug(f"HVAC mode set to {hvac_mode} for {self._device_name}")
            self.async_write_ha_state()


    def ble_callback(self, service_info: BluetoothServiceInfoBleak, change: BluetoothChange):
        _LOGGER.debug("BLE advertisement received: %s (%s)", service_info.address, service_info.manufacturer_id)

        # We have two different types of advertising
        # 1. Real temperature
        # 2. Set temperatur

        decrypted_current = decrypt_current_temperature(service_info)
        if decrypted_current:
            # This packet is the real temperature
            self.set_current_temperature(decrypted_current)
            return

        decrypted_set = decrypt_target_temperature(service_info)
        if decrypted_set:
            # This packet is the set temperature
            self.set_target_temperature(decrypted_set)
            return

        _LOGGER.debug("Unknown Package")


    def set_target_temperature(self, temperature):
        if temperature is not None:
            self._target_temperature = temperature
            self.schedule_update_ha_state()


    def set_current_temperature(self, temperature):
        if temperature is not None:
            self._current_temperature = temperature
            self.schedule_update_ha_state()


    def set_hvac_mode(self, hvac_mode):
        if hvac_mode in self.hvac_modes:
            self._hvac_mode = hvac_mode
            self.schedule_update_ha_state()


def decrypt_current_temperature(service_info: BluetoothServiceInfoBleak) -> float:
    manufacturer_data = service_info.manufacturer_data.get(MANUFACTURER_ID)

    if not manufacturer_data:
        return

    data_value = get_data_by_prefix(manufacturer_data, CURRENT_TEMPERATURE_PREFIX)

    if not data_value:
        return

    return convert_data_to_temperature(data_value)


def decrypt_target_temperature(service_info: BluetoothServiceInfoBleak) -> float:
    manufacturer_data = service_info.manufacturer_data.get(MANUFACTURER_ID)

    if not manufacturer_data:
        return

    data_value = get_data_by_prefix(manufacturer_data, TARGET_TEMPERATURE_PREFIX)

    if not data_value:
        return

    return convert_data_to_temperature(data_value)


def get_data_by_prefix(data, prefix):
    index = data.find(prefix)

    if index == -1:
        return

    if len(data) < (index + len(prefix) + TEMPERATURE_LENGTH_BYTES):
        _LOGGER.debug("Not enough data after broadcast prefix")
        return

    return data[(-1*TEMPERATURE_LENGTH_BYTES):]


def convert_data_to_temperature(data: bytearray) -> float:
    # Convert to integer
    value = int.from_bytes(data, byteorder='big')

    # This is reverse engineered from the advertising packages
    # Who does something like that?
    if value > 2048:
        temperature = float(value - 2048) / 50.0
    else:
        temperature = float(value) / 100.0

    return temperature