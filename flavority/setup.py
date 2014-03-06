
from setuptools import setup, find_packages
import os
import re

here = os.path.abspath(os.path.dirname(__file__))

# Read the version number from a source file.
# Code taken from pip's setup.py
def find_version(*file_paths):
    with open(os.path.join(here, *file_paths), 'r') as f:
        version_file = f.read()

    # The version line must have the form
    # __version__ = 'ver'
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name="flavority-api",
    version = find_version('flavority', '__init__.py'),
    description = "server for flavority offering a RESTful API",

    # TODO: license

    classifiers = [
        'Development Status :: 1 - Planning',

        'Framework :: Flask',
        'Environment :: Console',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Intended Audience :: End Users/Desktop',
        
        # TODO: license
        
        'Natural Language :: English',
        
        'Operating System :: OS Independent',

        'Programming Language :: Python :: 3',
    ],

    keywords = 'flavority recipe cookbook restful',

    install_requires = [
        "Flask>=0.10",
        "Flask-RESTful>=0.2.11",
        "Flask-SQLAlchemy>=1.0",
        "psycopg2>=2.5",
        "SQLAlchemy>=0.9",
    ],

    packages = find_packages(exclude = ["tests*"]),
)

