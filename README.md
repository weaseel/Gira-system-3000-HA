# Gira System 3000 Thermostat Integration

This is a custom component for [Home Assistant](https://www.home-assistant.io/) that integrates the **Gira System 3000 Thermostat** via Bluetooth Low Energy (BLE). It allows you to monitor ~~and control~~ the thermostat directly from Home Assistant.

## Overview

This integration provides a `climate` entity for the Gira System 3000 Thermostat. It listens to BLE advertisements to update the current and target temperatures ~~and allows setting the target temperature~~ via BLE.

## Features

- Display current temperature
- Display ~~and set~~ target temperature
- BLE-based communication
- ~~Basic HVAC mode support~~

## Installation

1. Create a directory `custom_components/gira_thermostat` in your Home Assistant configuration folder.
2. Copy the component files into this directory.
3. Restart Home Assistant.

## Configuration

This component uses a config entry and is set up via the UI or through discovery. No manual YAML configuration is required.

## Usage

Once installed and configured, the thermostat will appear as a climate entity in Home Assistant.
You can view the current temperature, set a target temperature, and monitor the HVAC mode.

## Limitations

- Only reads the advertising packages - no direct connection yet
- Only the `off` HVAC mode is currently supported. Reading the current status requires an active BLE connection.
- Requires BLE support and proximity to the Gira thermostat.

## License

This project is licensed under the MIT License.
