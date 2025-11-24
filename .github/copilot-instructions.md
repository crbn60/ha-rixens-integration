# Copilot Instructions for Rixens MCS7 Home Assistant Integration

This document provides instructions for GitHub Copilot coding agent to work effectively on this repository.

## Project Overview

This is a Home Assistant custom integration for the Rixens MCS7 hydronic heating controller. The integration:
- Polls `status.xml` from the controller for status updates
- Sends control commands via `interface.cgi?act=<id>&val=<value>`
- Provides UI-based configuration (Config Flow + Options Flow)
- Exposes entities for sensors, numbers (writable), and switches (writable)

## Project Structure

```
custom_components/rixens/   # Main integration code
├── __init__.py             # Integration setup and coordinator
├── api.py                  # API client for controller communication
├── config_flow.py          # UI configuration flows
├── const.py                # Constants, mappings, icons
├── coordinator.py          # DataUpdateCoordinator for polling
├── diagnostics.py          # Diagnostic data export
├── number.py               # Number entities (setpoint, fan speed)
├── sensor.py               # Read-only sensor entities
├── switch.py               # Switch entities (heat source enables)
├── manifest.json           # Integration metadata
├── services.yaml           # Service definitions (if any)
└── translations/           # i18n strings

tests/                      # Test suite
├── test_config_flow.py     # Config flow tests

docs/                       # Documentation
└── act_map.md             # ACT ID mapping reference
```

## Code Style and Standards

### Python Style
- **Black** formatter with 88 character line length
- **isort** for import sorting (black profile)
- **flake8** for linting (extends ignore: E203)
- Follow Home Assistant custom integration patterns
- Use type hints where appropriate
- Target Python 3.11+ (3.12 preferred)

### Code Quality Tools
- Pre-commit hooks are configured (`.pre-commit-config.yaml`)
- Run before committing: `pre-commit run --all-files`
- Manually run checks:
  - `black .` - Format code
  - `isort .` - Sort imports
  - `flake8` - Lint code

## Testing

### Running Tests
```bash
pytest -q
```

### Test Requirements
- All new features should include tests
- Focus areas:
  - Config flow (setup, options, validation)
  - XML parsing (especially fault codes, nested elements)
  - Write operations (numbers and switches)
  - Coordinator error handling
  - API client responses

### Test Infrastructure
- Uses `pytest` with `pytest-asyncio`
- `pytest-homeassistant-custom-component` for HA testing
- `aioresponses` for mocking HTTP calls

## Building and Validation

### Pre-commit Validation
```bash
pre-commit run --all-files
```

### HACS Validation
The integration is HACS-compatible. Ensure:
- `manifest.json` is properly formatted
- `hacs.json` is valid
- Version follows semantic versioning

## Development Workflow

1. **Make Changes**: Edit files in `custom_components/rixens/`
2. **Run Tests**: `pytest -q`
3. **Format Code**: `black .` and `isort .`
4. **Lint**: `flake8`
5. **Run Pre-commit**: `pre-commit run --all-files`
6. **Update Docs**: If adding entities or changing ACT mappings, update `README.md` and `docs/act_map.md`

## Integration-Specific Guidelines

### Entity Naming
- Use descriptive entity IDs: `sensor.rixens_<attribute>`, `number.rixens_<control>`, `switch.rixens_<enable>`
- Follow Home Assistant entity naming conventions

### XML Parsing
- Controller returns `status.xml` with nested elements
- Handle missing/malformed XML gracefully
- Parse fault codes with `FAULT_PREFIX` convention

### Control Commands
- Commands use ACT IDs defined in `CMD_MAP` (const.py)
- Validate ranges before sending (min/max for numbers)
- All write operations should be safe and validated

### Icons
- Use appropriate MDI icons from `ICON_MAP` (const.py)
- Add new mappings to `ICON_MAP` when introducing entities

### Polling
- DataUpdateCoordinator handles polling
- Configurable interval (2-3600 seconds, default 15)
- Handle network errors gracefully

## What NOT to Modify

### Protected Files
- **DO NOT** modify `.git/` or git history
- **DO NOT** change license terms in `LICENSE`
- **DO NOT** modify `.pre-commit-config.yaml` unless fixing a specific tool issue
- **DO NOT** commit secrets, API keys, or sensitive data
- **DO NOT** modify production controller settings or endpoints in examples

### Sensitive Areas
- Be cautious with control command ACT IDs - validate before changing
- Heating equipment control is sensitive - test thoroughly
- Don't introduce unsafe write operations without validation

## Home Assistant Integration Best Practices

### Coordinator Pattern
- Use DataUpdateCoordinator for polling (already implemented)
- Handle `UpdateFailed` exceptions properly
- Respect configured poll intervals

### Config Flow
- UI-based configuration only (no YAML)
- Validate user input (host, intervals)
- Provide clear error messages

### Entity Classes
- Inherit from appropriate HA base classes
- Implement required properties (`name`, `unique_id`, `device_info`)
- Use `@property` decorators for entity attributes
- Coordinate with DataUpdateCoordinator for state updates

### Diagnostics
- Redact sensitive data (IPs, network info)
- Include relevant controller state
- See `DIAGNOSTIC_KEYS` in const.py

## Documentation

### When to Update Docs
- Adding new entities → Update README.md entity table
- Changing ACT mappings → Update `docs/act_map.md`
- New configuration options → Update README.md configuration table
- Bug fixes or features → Consider updating CONTRIBUTING.md

### Documentation Style
- Use clear, concise language
- Include examples where helpful
- Keep tables aligned and readable
- Link to relevant HA documentation

## Common Tasks

### Adding a New Entity
1. Determine entity type (sensor/number/switch)
2. Add to appropriate platform file (`sensor.py`, etc.)
3. Update `ICON_MAP` in `const.py` if needed
4. Add ACT ID to `CMD_MAP` if writable
5. Add tests for the entity
6. Update README.md entity table

### Adding a Control Command
1. Verify ACT ID with controller
2. Add to `CMD_MAP` in `const.py`
3. Implement in appropriate platform
4. Add validation (min/max, allowed values)
5. Test write operations
6. Update `docs/act_map.md`

### Debugging
- Enable debug logging: `custom_components.rixens`
- Check coordinator update errors
- Validate XML responses
- Test with sanitized `status.xml` snippets

## Examples

### Entity Implementation Pattern
```python
class RixensSensor(SensorEntity):
    """Representation of a Rixens sensor."""

    def __init__(self, coordinator, field_name):
        self._coordinator = coordinator
        self._field_name = field_name

    @property
    def name(self):
        return f"Rixens {self._field_name.title()}"

    @property
    def state(self):
        return self._coordinator.data.get(self._field_name)
```

### Testing Pattern
```python
async def test_config_flow_success(hass):
    """Test successful configuration."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    assert result["type"] == "form"
```

## Contact and Support

- Issues: Use GitHub Issues for bugs and feature requests
- Include: Integration version, HA version, debug logs, sanitized XML
- PRs: Use `feature/<description>` branch naming
- Review: All changes require review before merge

## License

MIT License - contributions are licensed under MIT
