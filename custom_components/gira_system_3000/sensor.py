from homeassistant.components.sensor import SensorEntity
from homeassistant.const import TEMP_CELSIUS
from bleak import BleakScanner
import asyncio

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities([BLETemperatureSensor("Real"), BLETemperatureSensor("Set")])

class BLETemperatureSensor(SensorEntity):
    def __init__(self, sensor_type):
        self._sensor_type = sensor_type
        self._attr_name = f"BLE Thermostat {sensor_type} Temperature"
        self._attr_unit_of_measurement = TEMP_CELSIUS
        self._attr_state = None

    async def async_update(self):
        devices = await BleakScanner.discover()
        for d in devices:
            if "YourDeviceName" in d.name:
                decrypted_data = self.decrypt_ble_data(d)
                self._attr_state = decrypted_data[self._sensor_type]

    def decrypt_ble_data(self, device):
        # Your decryption logic here
        return {
            "Real": 21.5,
            "Set": 23.0
        }
