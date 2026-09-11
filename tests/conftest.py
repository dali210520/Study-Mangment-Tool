import pytest
from unittest.mock import patch

@pytest.fixture(autouse=True)
def disable_notifications_in_tests():
    """
    Mock Notification.objects.create globally for all tests.
    This prevents notifications from being created when objects (Tasks, Plans, etc.)
    are created during test setup. Since notifications are rendered in the global 
    base.html context via context processors, they can pollute the HTML response 
    content and cause UI list filter assertions (e.g. `assert 'Task' not in content`)
    to falsely fail.
    """
    with patch('apps.core.models.Notification.objects.create') as mock_create:
        yield mock_create
