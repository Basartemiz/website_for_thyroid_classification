"""
Pytest configuration for Django tests.
"""

import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')


def pytest_configure():
    """Configure Django settings for pytest."""
    settings.DEBUG = False
    django.setup()
