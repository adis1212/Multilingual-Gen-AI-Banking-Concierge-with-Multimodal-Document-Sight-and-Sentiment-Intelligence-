"""
pytest configuration for the backend test suite.
Enables asyncio mode so async test functions work without explicit event loop setup.
"""
import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as async")
