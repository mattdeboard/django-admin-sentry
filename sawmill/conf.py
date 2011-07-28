USE_L10N = True

LOGIN_URL = '/admin'

FILTERS = (
    'sawmill.filters.UserFilter',
    'sawmill.filters.ActionFilter',
    'sawmill.filters.ObjectFilter',
)       

CONTENT_TYPES = (
    (2, "Groups"),
    (3, "Users"),
    (7, "Sites"),
    (14, "Indices"),
    (15, "Social Links"),
    (19, "Configurations"),
    (20, "SEO Sites"),
    (21, "SEO Site Redirects"),
    (23, "Google Analytics"),
    (25, "Social Links"),
)

TEMPLATE_DIRS = (
    '/home/web/sawmill/templates/sawmill',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

USER_PROFILE_URL = '/admin/auth/user'
