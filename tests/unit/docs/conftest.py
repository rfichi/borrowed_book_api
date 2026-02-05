import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add the service directory to sys.path so imports work
SERVICE_PATH = str(Path(__file__).parents[3] / "services" / "docs")


@pytest.fixture(scope="module")
def docs_modules():
    """
    Sets up the environment for docs service tests.
    Imports modules and returns them.
    Cleans up sys.modules after usage.
    """
    if SERVICE_PATH not in sys.path:
        sys.path.insert(0, SERVICE_PATH)

    import main

    class Modules:
        pass

    modules = Modules()
    modules.main = main

    yield modules

    if SERVICE_PATH in sys.path:
        sys.path.remove(SERVICE_PATH)

    if "main" in sys.modules:
        del sys.modules["main"]


@pytest.fixture
def client(docs_modules):
    """
    Returns a TestClient for the docs service app.
    """
    return TestClient(docs_modules.main.app)
