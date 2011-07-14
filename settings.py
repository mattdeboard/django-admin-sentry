import os

USE_L10N = True

LOGIN_URL = '/admin'

FILTERS = (
        'admin_sentry.filters.UserFilter',
        'admin_sentry.filters.ObjectFilter',
)       

TEMPLATE_DIRS = (
        '/home/web/admin_sentry/templates/admin_sentry',
)

TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
)

