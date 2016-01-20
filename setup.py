try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

import versioneer


config = {
    'description': 'Manipulate third party resources and format data as necessary',
    'author': 'Matt Conley',
    'url': 'https://www.github.com/mtconley/clients.git
    'download_url': None, 
    'author_email': '',
    'version': '0.0.1',
    'install_requires': [], 
    'dependency_links': [],
    'packages': find_packages(),
    'scripts': [],
    'name': 'clients',
}

setup(**config)
