
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.bluetooth import async_register_callback, BluetoothScanningMode

DOMAIN = "gira_system_3000_thermostat"
MANUFACTURER_ID = 0x0584
TARGET_TEMPERATURE_PREFIX = bytearray.fromhex("F7006501FF1001")
CURRENT_TEMPERATURE_PREFIX = bytearray.fromhex("F7014101FE1001")
TEMPERATURE_LENGTH_BYTES = 2

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "device_name": entry.data["device_name"],
        "device_address": entry.data["device_address"],
        "entity": None  # will be set later
    }


    def ble_callback(service_info, change):
        entity = hass.data[DOMAIN][entry.entry_id]["entity"]
        if entity:
            entity.ble_callback(service_info, change)


    async_register_callback(
        hass,
        ble_callback,
        {"address": entry.data["device_address"]},
        BluetoothScanningMode.ACTIVE
    )

    await hass.config_entries.async_forward_entry_setups(entry, ["climate"])

    return True
