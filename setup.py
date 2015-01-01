from distutils.core import setup
from setuptools import find_packages

setup(name='checkmate',
version='0.0.1',
author=u'Andreas Dewes - QuantifiedCode UG (haftungsbeschränkt)',
author_email = 'andreas@quantifiedcode.com',
license = 'Affero GPL (AGPL)',
entry_points = {
        'console_scripts': [
               'checkmate = checkmate.scripts.manage:main',
        ],
    },
url='https://github.com/quantifiedcode/checkmate',
packages=find_packages(),
zip_safe = False,
)
