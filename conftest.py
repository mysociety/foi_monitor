"""
pytest configuration for foi_monitor.

Overrides django_db_setup to use the existing populated database
rather than creating a test database. This project tests against
the real source data from Cabinet Office and FOISA.
"""

import pytest


@pytest.fixture(scope="session")
def django_db_setup():
    """Override to skip test database creation — use the real database."""
    pass


@pytest.fixture(autouse=True)
def _enable_db_access(request, django_db_blocker):
    """
    Automatically allow database access for all tests.

    Since we use the real populated database (not a test DB),
    every test needs DB access.
    """
    django_db_blocker.unblock()
    yield
    django_db_blocker.restore()
