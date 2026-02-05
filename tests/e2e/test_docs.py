import pytest
import httpx


@pytest.mark.e2e
def test_docs_service_e2e(gateway_url):
    """
    E2E test for the Docs Service.
    Verifies that the service is reachable via the gateway (or configured URL)
    and enforces authentication.
    """
    # Use the /docs path on the gateway
    docs_url = f"{gateway_url}/docs"

    print(f"Testing Docs Service E2E at: {docs_url}")

    # 1. Test Unauthenticated Access
    with httpx.Client(verify=False) as client:
        resp = client.get(docs_url)
        assert (
            resp.status_code == 401
        ), f"Expected 401 for unauthenticated access, got {resp.status_code}"
        assert "Basic" in resp.headers.get(
            "WWW-Authenticate", ""
        ), "Expected Basic Auth challenge"

    # 2. Test Authenticated Access
    # We use admin:admin as hardcoded in the service
    auth = ("admin", "admin")
    with httpx.Client(verify=False, auth=auth) as client:
        resp = client.get(docs_url)
        assert (
            resp.status_code == 200
        ), f"Expected 200 for authenticated access, got {resp.status_code}"
        assert "<html" in resp.text.lower(), "Expected HTML response"
        assert "Borrowed Book API Docs" in resp.text, "Expected correct title in HTML"

    # 3. Test Health Check (if exposed via gateway)
    # Based on nginx/gateway config, usually only /docs is exposed or / is routed to docs service?
    # In api_gateway_config.yaml, we routed /docs to docs service.
    # We did NOT route / (root) of gateway to docs service root.
    # So we only test /docs here.
