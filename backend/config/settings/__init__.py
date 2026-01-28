"""
Django settings module.

This module automatically loads the appropriate settings based on the
DJANGO_SETTINGS_MODULE environment variable.

For development: config.settings.development (default)
For production: config.settings.production
"""

import os

# Default to development settings
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# If DJANGO_SETTINGS_MODULE points to this package, use development
if settings_module == 'config.settings':
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.development'
