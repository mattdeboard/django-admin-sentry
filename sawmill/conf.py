USE_L10N = True

LOGIN_URL = '/admin'

FILTERS = (
        'sawmill.filters.UserFilter',
        'sawmill.filters.ActionFilter',
)       

TEMPLATE_DIRS = (
        '/home/web/sawmill/templates/sawmill',
)

TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
)

USER_PROFILE_URL = '/admin/auth/user'
