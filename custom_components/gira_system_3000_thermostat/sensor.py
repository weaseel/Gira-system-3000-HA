#from homeassistant.components.sensor import SensorEntity
#from homeassistant.components.climate import ClimateEntity
#from homeassistant.components.bluetooth import async_register_callback, BluetoothChange
#from homeassistant.const import UnitOfTemperature
#from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
#import logging
#
#_LOGGER = logging.getLogger(__name__)
#
#MANUFACTURER_ID = 0x0584
#SET_TEMPERATURE_PREFIX = bytearray.fromhex("F7006501FF1001")
#REAL_TEMPERATURE_PREFIX = bytearray.fromhex("F7014101FE1001")
#TEMPERATURE_LENGTH_BYTES = 2
#
#
#async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
#    real_sensor = GiraThermostatSensor("Real")
#    set_sensor = GiraThermostatSensor("Set")
#    async_add_entities([real_sensor, set_sensor])
#
#    def ble_callback(service_info: BluetoothServiceInfoBleak, change: BluetoothChange):
#        _LOGGER.debug("BLE advertisement received: %s (%s)", service_info.address, service_info.manufacturer_id)
#
#        # We have two different types of advertising
#        # 1. Real temperature
#        # 2. Set temperatur
#
#        decrypted_real = decrypt_real_temperature(service_info)
#        if decrypted_real:
#            # This packet is the real temperature
#            real_sensor.update_value(decrypted_real)
#            return
#
#        decrypted_set = decrypt_set_temperature(service_info)
#        if decrypted_set:
#            # This packet is the set temperature
#            set_sensor.update_value(decrypted_set)
#
#    match_dict = {
#        #"manufacturer_id": MANUFACTURER_ID
#    }
#
#    async_register_callback(hass, ble_callback, match_dict, mode="advertisement")
#
#class GiraThermostatSensor(SensorEntity):
#    def __init__(self, sensor_type: str) -> None:
#        self._sensor_type = sensor_type
#        self._attr_name = f"Gira Thermostat {sensor_type} Temperature"
#        self._attr_unit_of_measurement = UnitOfTemperature.CELSIUS
#        self._attr_device_class = "temperature"
#        self._attr_native_value = None
#
#    def update_value(self, value: float | None) -> None:
#        if value is not None:
#            self._attr_native_value = float(value)  # ✅ Use this for newer HA versions
#            _LOGGER.debug("Updated %s temperature to %s", self._sensor_type, value)
#            self.async_write_ha_state()
#
#
#def decrypt_real_temperature(service_info: BluetoothServiceInfoBleak) -> float:
#    manufacturer_data = service_info.manufacturer_data.get(MANUFACTURER_ID)
#
#    if not manufacturer_data:
#        return
#
#    data_value = get_data_by_prefix(manufacturer_data, REAL_TEMPERATURE_PREFIX)
#
#    if not data_value:
#        return
#
#    return convert_data_to_temperature(data_value)
#
#def decrypt_set_temperature(service_info: BluetoothServiceInfoBleak) -> float:
#    manufacturer_data = service_info.manufacturer_data.get(MANUFACTURER_ID)
#
#    if not manufacturer_data:
#        return
#
#    data_value = get_data_by_prefix(manufacturer_data, SET_TEMPERATURE_PREFIX)
#
#    if not data_value:
#        return
#
#    return convert_data_to_temperature(data_value)
#
#def get_data_by_prefix(data, prefix):
#    index = data.find(prefix)
#
#    if index == -1:
#        return
#
#    if len(data) < (index + len(prefix) + TEMPERATURE_LENGTH_BYTES):
#        _LOGGER.debug("Not enough data after broadcast prefix")
#        return
#
#    return data[(-1*TEMPERATURE_LENGTH_BYTES):]
#
#def convert_data_to_temperature(data: bytearray) -> float:
#    # Convert to integer
#    value = int.from_bytes(data, byteorder='big')
#
#    # This is reverse engineered from the advertising packages
#    temperature = float(value - 2048) / 50.0
#
#    return temperature
