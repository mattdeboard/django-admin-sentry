USE_L10N = True

LOGIN_URL = '/admin'

FILTERS = (
    'admin_sentry.filters.UserFilter',
    'admin_sentry.filters.ActionFilter',
    'admin_sentry.filters.ObjectFilter',
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

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

USER_PROFILE_URL = '/admin/auth/user'
