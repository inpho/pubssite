import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'MySQL-python',
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'pyramid_mako',
    'pystache',
    'zope.sqlalchemy',
    'waitress',
    'wtforms',
    'webhelpers',
    'requests',
    'rython',
    'redis'
    ]

setup(name='pubssite',
      version='0.0',
      description='pubssite',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='pubssite',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = pubssite:main
      [console_scripts]
      initialize_pubssite_db = pubssite.scripts.initializedb:main
      """,
      )

