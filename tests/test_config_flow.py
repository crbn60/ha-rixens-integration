"""Tests for the Rixens config flow."""

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType, InvalidData

from custom_components.rixens.const import (
    CONF_HOST,
    CONF_POLL_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
    MAX_POLL_INTERVAL,
    MIN_POLL_INTERVAL,
)


@pytest.mark.asyncio
async def test_user_flow_success(hass: HomeAssistant) -> None:
    """Test successful user flow with valid input."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_HOST: "192.168.1.100"}
    )
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Rixens MCS7 (192.168.1.100)"
    assert result2["data"] == {CONF_HOST: "192.168.1.100"}
    assert result2["options"] == {CONF_POLL_INTERVAL: DEFAULT_POLL_INTERVAL}


@pytest.mark.asyncio
async def test_user_flow_host_with_whitespace(hass: HomeAssistant) -> None:
    """Test user flow strips whitespace from host."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_HOST: "  192.168.1.100  "}
    )
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"] == {CONF_HOST: "192.168.1.100"}


@pytest.mark.asyncio
async def test_user_flow_empty_host(hass: HomeAssistant) -> None:
    """Test user flow with empty host shows error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_HOST: ""}
    )
    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {CONF_HOST: "invalid_host"}


@pytest.mark.asyncio
async def test_user_flow_whitespace_only_host(hass: HomeAssistant) -> None:
    """Test user flow with whitespace-only host shows error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_HOST: "   "}
    )
    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {CONF_HOST: "invalid_host"}


@pytest.mark.asyncio
async def test_user_flow_duplicate_host(hass: HomeAssistant) -> None:
    """Test user flow aborts when host is already configured."""
    # First entry
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_HOST: "192.168.1.100"}
    )

    # Try to add same host again
    result2 = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result3 = await hass.config_entries.flow.async_configure(
        result2["flow_id"], user_input={CONF_HOST: "192.168.1.100"}
    )
    assert result3["type"] == FlowResultType.ABORT
    assert result3["reason"] == "already_configured"


@pytest.mark.asyncio
async def test_user_flow_case_insensitive_duplicate(hass: HomeAssistant) -> None:
    """Test user flow treats hosts as case-insensitive for duplicates."""
    # First entry with lowercase
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_HOST: "mcs7.local"}
    )

    # Try to add same host with different case
    result2 = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result3 = await hass.config_entries.flow.async_configure(
        result2["flow_id"], user_input={CONF_HOST: "MCS7.LOCAL"}
    )
    assert result3["type"] == FlowResultType.ABORT
    assert result3["reason"] == "already_configured"


@pytest.mark.asyncio
async def test_import_flow_not_supported(hass: HomeAssistant) -> None:
    """Test that import from YAML is not supported."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_IMPORT},
        data={CONF_HOST: "192.168.1.100"},
    )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "import_not_supported"


@pytest.mark.asyncio
async def test_options_flow_success(hass: HomeAssistant, mock_config_entry) -> None:
    """Test options flow with valid poll interval."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={CONF_POLL_INTERVAL: 30}
    )
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"] == {CONF_POLL_INTERVAL: 30}


@pytest.mark.asyncio
async def test_options_flow_min_interval(
    hass: HomeAssistant, mock_config_entry
) -> None:
    """Test options flow with minimum poll interval."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={CONF_POLL_INTERVAL: MIN_POLL_INTERVAL}
    )
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"] == {CONF_POLL_INTERVAL: MIN_POLL_INTERVAL}


@pytest.mark.asyncio
async def test_options_flow_max_interval(
    hass: HomeAssistant, mock_config_entry
) -> None:
    """Test options flow with maximum poll interval."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={CONF_POLL_INTERVAL: MAX_POLL_INTERVAL}
    )
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"] == {CONF_POLL_INTERVAL: MAX_POLL_INTERVAL}


@pytest.mark.asyncio
async def test_options_flow_interval_too_low(
    hass: HomeAssistant, mock_config_entry
) -> None:
    """Test options flow with poll interval below minimum.

    Note: The NumberSelector enforces min/max at the schema level,
    so invalid values are caught during schema validation.
    """
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)

    # The schema validation will catch this and raise InvalidData
    # This is the expected behavior with NumberSelector
    with pytest.raises(InvalidData):
        await hass.config_entries.options.async_configure(
            result["flow_id"], user_input={CONF_POLL_INTERVAL: MIN_POLL_INTERVAL - 1}
        )


@pytest.mark.asyncio
async def test_options_flow_interval_too_high(
    hass: HomeAssistant, mock_config_entry
) -> None:
    """Test options flow with poll interval above maximum.

    Note: The NumberSelector enforces min/max at the schema level,
    so invalid values are caught during schema validation.
    """
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)

    # The schema validation will catch this and raise InvalidData
    # This is the expected behavior with NumberSelector
    with pytest.raises(InvalidData):
        await hass.config_entries.options.async_configure(
            result["flow_id"], user_input={CONF_POLL_INTERVAL: MAX_POLL_INTERVAL + 1}
        )


@pytest.mark.asyncio
async def test_options_flow_uses_existing_value(
    hass: HomeAssistant, mock_config_entry
) -> None:
    """Test options flow shows existing poll interval value."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    # The default value in the schema should be the current option value
    assert CONF_POLL_INTERVAL in result["data_schema"].schema


@pytest.mark.asyncio
async def test_multiple_instances(hass: HomeAssistant) -> None:
    """Test that multiple instances can be configured with different hosts."""
    # Configure first instance
    result1 = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    entry1 = await hass.config_entries.flow.async_configure(
        result1["flow_id"], user_input={CONF_HOST: "192.168.1.100"}
    )
    assert entry1["type"] == FlowResultType.CREATE_ENTRY

    # Configure second instance with different host
    result2 = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    entry2 = await hass.config_entries.flow.async_configure(
        result2["flow_id"], user_input={CONF_HOST: "192.168.1.101"}
    )
    assert entry2["type"] == FlowResultType.CREATE_ENTRY

    # Verify both entries exist
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 2
    hosts = {entry.data[CONF_HOST] for entry in entries}
    assert hosts == {"192.168.1.100", "192.168.1.101"}
