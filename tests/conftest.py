# tests/conftest.py
import pytest
from unittest.mock import patch


# This prevents tests from making real HTTP requests
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


# A reusable fixture with your sample XML
@pytest.fixture
def mock_status_xml():
    return """<response>
<version>TEST_VERSION</version>
<uptime>12345</uptime>
<systemheat>1</systemheat>
<currenttemp>145</currenttemp>
<heater1>
    <battv>128</battv>
    <flametemp>5000</flametemp>
    <inlettemp>150</inlettemp>
    <outlettemp>160</outlettemp>
</heater1>
<settings>
    <setpoint>135</setpoint>
    <fanspeed>25</fanspeed>
    <floorenable>1</floorenable>
</settings>
</response>"""
