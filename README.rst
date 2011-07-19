=============
Admin Sentry
=============

Admin Sentry is an interactive admin log viewer modeled heavily on David Cramer's `django-sentry <https://github.com/dcramer/django-sentry>`_.

As of this sub-1.0 release, interaction with the admin logging system is fairly limited, but it is more robust than the default system. (Admittedly, this isn't saying much.)

-------------
Installation
-------------

First, install the package:

  `$ pip install git+git://github.com/mattdeboard/django-admin-sentry.git`

Then, add `admin_sentry` to your package's INSTALLED_APPS setting.

Finally, add the following lines to your project's `urls.py`:

  import admin_sentry

  urlpatterns = pattern('',
  ...
  (r'^admin_sentry/', include('admin_sentry.urls')),
  ...


-----------
Logging in
-----------

To access admin_sentry, you must be logged in to your project's admin panel. Once you are logged in, navigate to `yourdomain.com/admin_sentry`. You'll then see the interface.

This admittedly convoluted process will likely be changed in the near future, allowing you to log directly in to admin_sentry to access these logs.
