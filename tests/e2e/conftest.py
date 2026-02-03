import os
import pytest


@pytest.fixture(scope="session")
def api_key():
    key = os.getenv("API_KEY")
    if not key:
        pytest.fail("API_KEY environment variable not set.")
    return key


@pytest.fixture(scope="session")
def gateway_url():
    return os.getenv("GATEWAY_URL", "https://borrow-gateway-bwzk395v.uc.gateway.dev")


@pytest.fixture(scope="session")
def headers(api_key):
    return {"x-api-key": api_key}
