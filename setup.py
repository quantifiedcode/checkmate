from distutils.core import setup
from setuptools import find_packages

setup(name='checkmate',
version='0.0.1',
author='Andreas Dewes - 7scientists',
author_email = 'andreas@7scientists.com',
license = 'MIT',
entry_points = {
        'console_scripts': [
            'checkmate = checkmate.scripts.manage:main',
        ],
    },
url='https://github.com/adewes/python-checkmate',
packages=find_packages(),
zip_safe = False,
)
