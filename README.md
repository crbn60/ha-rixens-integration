# Rixens MCS7 Home Assistant Integration

[![CI Status](https://github.com/crbn60/ha-rixens-integration/actions/workflows/ci.yml/badge.svg)](https://github.com/crbn60/ha-rixens-integration/actions/workflows/ci.yml)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen.svg)](https://pre-commit.com/)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB)

> Custom integration for the Rixens MCS7 hydronic heating controller, exposing status, temperatures, fan control, heat source flags, and more to Home Assistant with bidirectional control where supported.

## Overview
Polls `status.xml` and sends control commands via `interface.cgi?act=<id>&val=<value>`. Configuration is UI-based (Config Flow + Options Flow); no YAML needed.

Core goals:
- Robust polling (DataUpdateCoordinator)
- Clean entity modeling (sensor, number, switch)
- Safe write operations with validation
- Icons for clear dashboards
- HACS-ready packaging

## Features
| Area | Read | Write | Notes |
|------|------|-------|-------|
| Temperature & Humidity | ✅ | ❌ | Scaling configurable later |
| Setpoint / Fan Speed | ✅ | ✅ | Numbers with range enforcement |
| Heat Source Enables | ✅ | ✅ | Switches (engine, electric, floor, etc.) |
| Fault Codes | ✅ | ❌ | Exposed as sensors (binary platform planned) |
| Diagnostics (network, runtime) | ✅ | ❌ | Redacted in diagnostics export |

## Installation (HACS Custom Repository)
1. Install HACS.
2. Add custom repo: `https://github.com/crbn60/ha-rixens-integration` (Integration category).
3. Install, restart Home Assistant.
4. Add integration via UI and set host/poll interval.

## Configuration
| Option | Purpose | Range | Default |
|--------|---------|-------|---------|
| Host/IP | Controller location | — | (required) |
| Poll Interval | Fetch frequency (s) | 2–3600 | 15 |

## Entity Preview
| Entity | Type | Writable | Source |
|--------|------|----------|--------|
| sensor.rixens_current_temperature | sensor | ❌ | currenttemp |
| sensor.rixens_current_humidity | sensor | ❌ | currenthumidity |
| number.rixens_setpoint | number | ✅ | setpoint |
| number.rixens_fan_speed | number | ✅ | fanspeed |
| switch.rixens_engineenable | switch | ✅ | engineenable |
| switch.rixens_electricenable | switch | ✅ | electricenable |
| switch.rixens_floorenable | switch | ✅ | floorenable |
| sensor.rixens_heater_state_code | sensor | ❌ | heaterstate |
| sensor.rixens_fault_AF | sensor | ❌ | fault_* |

## Entity Mapping & Configuration
See [docs/entity_mapping.md](docs/entity_mapping.md) for comprehensive entity definitions, scaling factors, and icon mappings.

## Control Mapping (Provisional)
See [docs/act_map.md](docs/act_map.md) for ACT IDs.

## Disclaimer
Heating equipment control can be sensitive. Use sane intervals and validate commands manually before automating.

## Contributing
See CONTRIBUTING.md. Issues welcome for mapping updates, new entities, and enhancements.

## License
MIT License (see LICENSE).

---
Initial scaffold; details will evolve.