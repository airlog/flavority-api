
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
    name="flavoritybot",
    version = find_version('flavoritybot', '__init__.py'),
    description = "downloading recipes from allrecipes.com",

    # TODO: license

    classifiers = [
        'Development Status :: 3 - Alpha',

        'Environment :: Console',
        'Topic :: Internet',
        
        # TODO: license
        
        'Natural Language :: English',
        
        'Operating System :: OS Independent',

        'Programming Language :: Python :: 3',
    ],

    keywords = 'movie video find subtitles',

    install_requires = [
        "beautifulsoup4",
    ],

    packages = find_packages(exclude = ["tests*"]),
)

