# Contributing to Rixens MCS7 Integration

## Development Environment
Use the DevContainer or Codespaces for a preconfigured Python 3.12 setup.

1. Clone the repo or open in Codespaces.
2. DevContainer installs dependencies and pre-commit hooks automatically.

## Running Home Assistant Locally
Copy or symlink `custom_components/rixens` into your local HA config directory:
```
hass --debug
```

## Testing
```
pytest -q
```
Add tests for:
- Config flow
- XML parsing (faults, nested elements)
- Write operations (numbers / switches)
- Coordinator error handling

## Code Style
Black, isort, and flake8 are enforced via pre-commit.

## Branching & PRs
Use `feature/<short-description>` and keep changes focused. Update docs (README, act_map) when adding entities or ACT mappings.

## Control Mapping
Adjust `CMD_MAP` in `const.py` once ACT IDs are verified. Update `docs/act_map.md`.

## Reporting Issues
Include:
- Integration version & HA version
- Debug logs (enable `custom_components.rixens`)
- Sanitized `status.xml` snippet

## License
MIT License. Contributions are licensed under MIT.
