try:
    from setuptools import setup, find_packages, Command
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages, Command

install_requires = ['django-paging>=0.2.4']

try:
    __import__('uuid')
except ImportError:
    install_requires.append('uuid')

setup(
    name='django-admin-sentry',
    version='1.0',
    author='Matt DeBoard',
    author_email='mattdeboard@gmail.com',
    include_package_data=True,
    packages=['admin_sentry'],
    install_required=install_requires,
)




