# Config Flow Development Guide

This guide is for contributors who want to understand or modify the Rixens integration's configuration flow.

## Architecture Overview

The Rixens integration uses Home Assistant's modern **Config Flow** pattern for UI-based configuration. This consists of:

1. **ConfigFlow** (`RixensConfigFlow`) - Handles initial setup
2. **OptionsFlow** (`RixensOptionsFlow`) - Handles configuration options
3. **Config Entry** - Stores configuration data
4. **Translations** - UI strings for the config flow

## File Structure

```
custom_components/rixens/
├── config_flow.py          # Config flow implementation
├── const.py                # Constants (domains, defaults, ranges)
├── translations/
│   └── en.json            # English translations for UI
└── manifest.json          # Integration metadata

tests/
├── conftest.py            # Test fixtures
└── test_config_flow.py    # Config flow tests
```

## Config Flow Implementation

### RixensConfigFlow

Located in `custom_components/rixens/config_flow.py`

#### Key Methods

**`async_step_user()`**
- Entry point for user-initiated configuration
- Presents a form with host/IP input field
- Validates input and creates config entry
- Uses `TextSelector` for modern UI

**`async_step_import()`**
- Handles YAML import (intentionally disabled)
- Always aborts with "import_not_supported"

**`async_get_options_flow()`**
- Static method that returns options flow handler
- Called by Home Assistant when user clicks "Configure"

#### Validation Logic

```python
# Host validation
host = user_input[CONF_HOST].strip()
if not host:
    errors[CONF_HOST] = "invalid_host"

# Unique ID for multi-instance support
await self.async_set_unique_id(host.lower())
self._abort_if_unique_id_configured()
```

Key points:
- Host is trimmed of whitespace
- Empty strings are rejected
- Unique ID is lowercase for case-insensitive comparison
- Prevents duplicate entries for same controller

### RixensOptionsFlow

Located in `custom_components/rixens/config_flow.py`

#### Key Methods

**`async_step_init()`**
- Presents options form with polling interval
- Uses `NumberSelector` with min/max validation
- Validates range (2-3600 seconds)
- Returns updated options

#### Validation Logic

```python
poll_interval = user_input[CONF_POLL_INTERVAL]
if poll_interval < MIN_POLL_INTERVAL or poll_interval > MAX_POLL_INTERVAL:
    errors[CONF_POLL_INTERVAL] = "interval_out_of_range"
```

**Note:** The `NumberSelector` also enforces min/max at the schema level, so most invalid values are caught before reaching this code. The manual validation serves as a safety net.

## Typed Schemas and Selectors

The integration uses Home Assistant's modern selector pattern for better UI:

### TextSelector (Host Input)

```python
data_schema = vol.Schema(
    {
        vol.Required(CONF_HOST): selector.TextSelector(
            selector.TextSelectorConfig(
                type=selector.TextSelectorType.TEXT,
            )
        ),
    }
)
```

Benefits:
- Consistent UI across Home Assistant
- Better mobile experience
- Automatic browser validation

### NumberSelector (Polling Interval)

```python
data_schema = vol.Schema(
    {
        vol.Required(
            CONF_POLL_INTERVAL,
            default=self.config_entry.options.get(
                CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL
            ),
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=MIN_POLL_INTERVAL,
                max=MAX_POLL_INTERVAL,
                mode=selector.NumberSelectorMode.BOX,
                unit_of_measurement="seconds",
            )
        ),
    }
)
```

Benefits:
- Enforces min/max in UI
- Shows unit of measurement
- Number box mode for easy input
- Default value pre-filled

## Constants

Located in `custom_components/rixens/const.py`

```python
DOMAIN = "rixens"
CONF_HOST = "host"
CONF_POLL_INTERVAL = "poll_interval"

DEFAULT_POLL_INTERVAL = 15
MIN_POLL_INTERVAL = 2
MAX_POLL_INTERVAL = 3600
```

All validation ranges are defined here for consistency.

## Translations

Located in `custom_components/rixens/translations/en.json`

Structure:
```json
{
  "config": {
    "step": { ... },      // Form titles and descriptions
    "error": { ... },     // Error messages
    "abort": { ... }      // Abort reasons
  },
  "options": {
    "step": { ... },
    "error": { ... }
  }
}
```

### Translation Keys

Each string has a key that maps to the code:

- `step.user.title` - Form title
- `step.user.description` - Form description
- `step.user.data.host` - Field label
- `error.invalid_host` - Error message
- `abort.already_configured` - Abort reason

## Testing

### Test Structure

Located in `tests/test_config_flow.py`

Categories of tests:
1. **User Flow Tests** - Initial setup scenarios
2. **Options Flow Tests** - Configuration update scenarios
3. **Validation Tests** - Edge cases and error conditions
4. **Multi-Instance Tests** - Multiple controller support

### Key Test Patterns

**Basic Flow Test**
```python
@pytest.mark.asyncio
async def test_user_flow_success(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_HOST: "192.168.1.100"}
    )
    assert result2["type"] == FlowResultType.CREATE_ENTRY
```

**Validation Test**
```python
@pytest.mark.asyncio
async def test_user_flow_empty_host(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_HOST: ""}
    )
    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {CONF_HOST: "invalid_host"}
```

**Options Flow Test**
```python
@pytest.mark.asyncio
async def test_options_flow_success(hass: HomeAssistant, mock_config_entry) -> None:
    mock_config_entry.add_to_hass(hass)
    
    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={CONF_POLL_INTERVAL: 30}
    )
    assert result2["type"] == FlowResultType.CREATE_ENTRY
```

### Test Fixtures

Located in `tests/conftest.py`

**`enable_custom_integrations`**
- Enables loading of custom integrations in tests
- Automatically used by all tests

**`mock_config_entry`**
- Provides a pre-configured config entry for testing
- Can be added to hass with `mock_config_entry.add_to_hass(hass)`

### Running Tests

```bash
# Run all config flow tests
pytest tests/test_config_flow.py -v

# Run specific test
pytest tests/test_config_flow.py::test_user_flow_success -v

# Run with coverage
pytest tests/test_config_flow.py --cov=custom_components.rixens.config_flow
```

## Multi-Instance Support

The integration supports multiple controllers through unique IDs:

```python
await self.async_set_unique_id(host.lower())
self._abort_if_unique_id_configured()
```

- Each controller has a unique ID based on its host (lowercase)
- Duplicate detection is case-insensitive
- Each instance maintains separate options (polling interval)
- Entity IDs are automatically made unique by Home Assistant

## Common Development Tasks

### Adding a New Config Option

1. **Add constant** to `const.py`:
   ```python
   CONF_NEW_OPTION = "new_option"
   DEFAULT_NEW_OPTION = "default_value"
   ```

2. **Update options flow** in `config_flow.py`:
   ```python
   data_schema = vol.Schema({
       vol.Required(CONF_POLL_INTERVAL, ...): ...,
       vol.Optional(
           CONF_NEW_OPTION,
           default=self.config_entry.options.get(CONF_NEW_OPTION, DEFAULT_NEW_OPTION)
       ): selector.TextSelector(...),
   })
   ```

3. **Add translation** in `translations/en.json`:
   ```json
   {
     "options": {
       "step": {
         "init": {
           "data": {
             "new_option": "New Option Label"
           }
         }
       }
     }
   }
   ```

4. **Add tests**:
   ```python
   @pytest.mark.asyncio
   async def test_options_flow_new_option(hass, mock_config_entry):
       # Test the new option
   ```

5. **Use in coordinator** or other components

### Adding Validation

1. **Add validation logic** in the flow method:
   ```python
   new_option = user_input[CONF_NEW_OPTION]
   if not validate_new_option(new_option):
       errors[CONF_NEW_OPTION] = "invalid_new_option"
   ```

2. **Add error translation**:
   ```json
   {
     "options": {
       "error": {
         "invalid_new_option": "New option must meet criteria..."
       }
     }
   }
   ```

3. **Add validation tests**

## Best Practices

### Code Style
- Use type hints for all parameters and return values
- Add docstrings to classes and methods
- Follow Home Assistant's coding standards
- Use logging for important events

### Validation
- Always validate user input
- Provide clear error messages
- Use selectors with built-in validation when possible
- Test edge cases

### Testing
- Test all paths (success, validation errors, aborts)
- Test edge cases (empty strings, whitespace, boundaries)
- Test multi-instance scenarios
- Use descriptive test names

### Translations
- Keep UI strings in translations, not code
- Provide helpful descriptions
- Use consistent terminology
- Consider internationalization (other languages)

## Debugging Tips

### Enable Debug Logging

Add to `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.rixens: debug
```

### Check Config Entry

In tests or live system:
```python
# List all config entries
entries = hass.config_entries.async_entries(DOMAIN)
for entry in entries:
    print(f"Entry: {entry.entry_id}")
    print(f"Data: {entry.data}")
    print(f"Options: {entry.options}")
```

### Test in Development Container

Use the `.devcontainer` setup for isolated testing.

## Resources

- [Home Assistant Config Flow Documentation](https://developers.home-assistant.io/docs/config_entries_config_flow_handler/)
- [Home Assistant Selectors](https://developers.home-assistant.io/docs/data_entry_flow_index/#show-form)
- [Testing Config Flows](https://developers.home-assistant.io/docs/development_testing/)
- [Translation Guide](https://developers.home-assistant.io/docs/internationalization/)

## Checklist for Config Flow Changes

- [ ] Update constants if needed
- [ ] Modify config flow logic
- [ ] Update translations
- [ ] Add/update tests
- [ ] Run linting (black, isort, flake8)
- [ ] Run all tests
- [ ] Test manually in Home Assistant
- [ ] Update documentation
- [ ] Update CONTRIBUTING.md if needed
