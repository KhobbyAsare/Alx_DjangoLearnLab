"""
Settings package initialization.
Automatically loads the appropriate settings module based on the environment.
"""

import os

# Determine which settings to use based on environment
environment = os.environ.get('DJANGO_ENVIRONMENT', 'development')

if environment == 'production':
    from .production import *
elif environment == 'development':
    from .development import *
else:
    # Default to development settings
    from .development import *
