==============
Django-Sawmill
==============

Sawmill is an interactive admin log viewer designed to let you do something useful with your logs.

As of this sub-1.0 release, interaction with the admin logging system is fairly limited, but it is more robust than the default system. (Admittedly, this isn't saying much.)

Also included is a LogEntryAdmin view, so your log entries will be browsable from the normal admin panel. :)

-------------
Installation
-------------

First, install the package:

  `$ pip install git+git://github.com/mattdeboard/django-admin-sentry.git`

Then, add the following to your package's settings.INSTALLED_APPS:

  'paging',
  'admin_sentry',

'paging' must precede 'admin_sentry'.
  
Finally, add the following lines to your project's `urls.py`:

  import admin_sentry

  urlpatterns = pattern('',
  ...
  (r'^admin_sentry/', include('admin_sentry.urls')),
  ...


-----------
Logging in
-----------

Navigate to `yourdomain.com/admin_sentry`. If you are not logged into your app's admin panel, you'll be prompted to log in. Once you do, you'll then see the interface.


--------
Credits
--------

Sawmill is modeled on heavily David Cramer's excellent `django-sentry <https://github.com/dcramer/django-sentry>`_. If you are familiar with Sentry then Sawmill will not seem foreign to you whatsoever.
