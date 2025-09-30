
import asyncio
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    async_register_callback,
    BluetoothScanningMode,
    BluetoothServiceInfoBleak,
    BluetoothChange,
)
from homeassistant.core import callback
from . import DOMAIN, MANUFACTURER_ID, TARGET_TEMPERATURE_PREFIX, CURRENT_TEMPERATURE_PREFIX, TEMPERATURE_LENGTH_BYTES

_LOGGER = logging.getLogger(__name__)

class GiraThermostatConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Gira Thermostat."""

    VERSION = 1

    def __init__(self):
        self._discovered = {}
        self._callback_registered = False


    async def async_step_user(self, user_input=None):
        """Initial step to start scanning."""
        return await self.async_step_scan()


    async def async_step_scan(self, user_input=None):
        """Scan for devices and allow selection or refresh."""
        existing_addresses = {
            entry.data["device_address"]
            for entry in self._async_current_entries()
        }

        # Handle user selection
        if user_input:
            selected = user_input.get("device_choice")
            if selected == "refresh":
                return await self.async_step_scan()
            else:
                selected_info = self._discovered.get(selected)
                if selected_info:
                    return self.async_create_entry(
                        title=selected_info.name or "Gira Thermostat",
                        data={
                            "device_address": selected_info.address,
                            "device_name": selected_info.name or "Gira Thermostat"
                        }
                    )

        if not self._callback_registered:
            def _device_callback(service_info: BluetoothServiceInfoBleak, change: BluetoothChange):
                if self.is_gira_thermostat_device(service_info) and service_info.address not in existing_addresses:
                    self._discovered[self.get_adress_string(service_info)] = service_info

            async_register_callback(
                self.hass,
                _device_callback,
                {"connectable": True},
                BluetoothScanningMode.ACTIVE
            )
            self._callback_registered = True

        await asyncio.sleep(1)

        # Build selection options

        device_options = {}
        for addr, info in self._discovered.items():
            unique_id_string = self.get_adress_string(info)
            device_options[unique_id_string] = f"{info.name or 'Unknown'} (RSSI: {info.rssi} ID: {unique_id_string})"


        # Add refresh option
        device_options["refresh"] = "Refresh device list"

        return self.async_show_form(
            step_id="scan",
            data_schema=vol.Schema({
                vol.Required("device_choice", default="refresh"): vol.In(device_options),
            }),
            description_placeholders={
                "device_summary": f"{len(self._discovered)} device(s) found."
            },
            last_step=False
        )


    def get_adress_string(self, info):
        unique_id = info.manufacturer_data.get(MANUFACTURER_ID)[0:4]
        unique_id_string = "".join(f"{b:02X}" for b in unique_id)
        return unique_id_string


    def is_gira_thermostat_device(self, service_info: BluetoothServiceInfoBleak) -> bool:
        # Customize this to match your advertising pattern
        manufacturer_data = service_info.manufacturer_data.get(MANUFACTURER_ID)

        if not manufacturer_data:
            return False

        if (manufacturer_data.find(TARGET_TEMPERATURE_PREFIX) != -1) or (manufacturer_data.find(CURRENT_TEMPERATURE_PREFIX) != -1):
            return True

        return False
