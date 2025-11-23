# Copilot Instructions — Rixens Integration

This file gives an AI coding agent the essential, repo-specific knowledge to be productive working on the `rixens` Home Assistant custom integration.

**Purpose & Big Picture**

- **Integration type:** Local-polling Home Assistant integration that reads `status.xml` and writes commands to `interface.cgi` on a Rixens/MCS7 controller.
- **Primary runtime flow:** `RixensApiClient` fetches and parses XML → `RixensCoordinator` (DataUpdateCoordinator) schedules periodic updates → platform entities (`sensor`, `number`, `switch`) read `coordinator.data` for values and call `api.set_parameter` to write commands.

**Key Files & What They Show**

- `custom_components/rixens/__init__.py`: API client, XML parsing, coordinator setup, and config entry lifecycle. Note: uses `yarl` for URL joining.
- `custom_components/rixens/const.py`: `DOMAIN`, `RIXENS_URL` key, and `CMD_MAP` mapping of parameter names to action IDs used for control commands.
- `custom_components/rixens/sensor.py`: Sensor definitions, dividers for integer-to-float conversions, entity `unique_id` pattern `rixens_{key}`.
- `custom_components/rixens/number.py` and `switch.py`: Control entities that map keys → action IDs using `CMD_MAP` and call `coordinator.api.set_parameter(action_id, value)`.
- `custom_components/rixens/config_flow.py`: Config flow that validates the device by fetching XML via `RixensApiClient`.
- `manifest.json`: lists runtime requirement `yarl>=1.8.0` and `iot_class: local_polling`.
- `mock_device.py` and `scripts/develop`: Local mock server and developer startup script used for manual testing and development.

**Project-specific Conventions & Patterns**

- **Single base URL:** Config entry stores a single base URL under `RIXENS_URL` (string). `RixensApiClient` composes `status.xml` and `interface.cgi` from this base URL.
- **Polling interval option:** The integration exposes a `update_interval` (seconds) option via the config entry's Options flow. Default is 10, range is 2–3600. Set via UI or config entry options.
- **Action mapping:** `CMD_MAP` maps logical names (e.g., `setpoint`, `fanspeed`) to integer action IDs used by `interface.cgi` queries.
- **Numeric scaling:** Sensors return integers in the XML which are scaled in `SENSORS` (see `divider` in `sensor.py`, e.g., `currenttemp` uses 10 → 14.0°C for `140`).
- **Entity unique IDs:** Use `rixens_{key}` for entities (consistent across platforms).
- **Coordinator storage:** Config entries store the coordinator at `hass.data[DOMAIN][entry.entry_id]`. Platforms expect to access the coordinator — note inconsistency below.

**Important Implementation Notes / Gotchas**

- Platform modules (`sensor.py`, `number.py`, `switch.py`) call `coordinator = hass.data[DOMAIN]` in `async_setup_platform`. However, `async_setup_entry` stores the coordinator under `hass.data[DOMAIN][entry.entry_id]`. Be careful: code assumes a single coordinator object in `hass.data[DOMAIN]` while setup entry uses a dict keyed by `entry_id`. When editing or adding multi-instance support, follow Home Assistant best-practices: platforms should receive the `coordinator` via `async_forward_entry_setups` and use `async_setup_entry`/`CoordinatorEntity` patterns per `entry_id`.
- The polling interval is now settable via config entry options (`update_interval`), validated in the options flow (2–3600 seconds). The default is 10 seconds. Change in `config_flow.py` and test in `test_rixens.py`.
- Tests in `tests/test_rixens.py` use config entry setup only; legacy YAML setup is deprecated and removed.

**Developer Workflows & Commands**

- Install dependencies: `python3 -m pip install --upgrade --requirement requirements.txt` and `python3 -m pip install --upgrade --requirement requirements_test.txt`. (`scripts/setup` automates this.)
- Run local development HA with mock device: `./scripts/develop` — this will:
  - create `config/` and copy a template if needed,
  - set `PYTHONPATH` to include `custom_components`,
  - start `mock_device.py` on port 8000,
  - start `hass --config config --debug`.
- Run tests: `pytest -q` (project includes `pytest-homeassistant-custom-component` in `requirements_test.txt` and uses `aioresponses` for mocking HTTP).

**Network/Integration Examples**

- Fetch status: `GET http://<base>/status.xml` — parsed by `RixensApiClient._parse_xml` into flat keys like `currenttemp`, `battv`, `setpoint`, `fanspeed`, `floorenable`, `systemheat`.
- Control command: `GET http://<base>/interface.cgi?act=<id>&val=<value>` — `set_parameter` builds `params = {'act': action_id, 'val': int(value)}`.

**When Changing Code, Check**

- If altering action IDs, update `const.CMD_MAP` and `mock_device.ACT_MAP` in `mock_device.py` to keep tests/dev matching.
- If touching URL construction, keep `yarl.URL` usage consistent to avoid double-slashes.
- When changing coordinator storage or multi-instance behavior, update all platform `async_setup_platform` implementations to use the entry-based setup pattern.

If anything above is unclear or you want the doc to include more examples (unit-test snippets, example XML, or a checklist for adding a new entity), tell me which sections to expand and I'll iterate.
