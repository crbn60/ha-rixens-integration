# Contributing to Rixens

Thank you for your interest in contributing! This project uses a **`dev`** branch for all ongoing development.

## Development Environment

This project uses **VS Code Dev Containers** for a consistent environment.

### Setup Steps

1. **Fork** this repository (`crbn60/ha-rixens-integration`).
2. Open the cloned folder in **VS Code**.
3. Click **"Reopen in Container"** when prompted.

## Local Testing Workflow

1. **Start Home Assistant:** In a terminal inside the container, run:

```bash
hass -c ./config
```

*Note: The mock server (`mock_device.py`) is automatically started in the background when the container launches and is accessible by Home Assistant.*

2. **Run Tests:** Before submitting, ensure all tests pass:

```bash
pytest tests/
```
