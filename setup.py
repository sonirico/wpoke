import io
from collections import OrderedDict

from setuptools import setup

with io.open('requirements.txt', 'rt', encoding='utf8') as f:
    install_requires = f.readlines()

setup(
    name='wpoke',
    version='0.1.0',
    url='https://pypi.org/project/wpoke/',
    project_urls=OrderedDict((
        ('Code', 'https://github.com/sonirico/wpoke/'),
        ('Issue tracker', 'https://github.com/sonirico/wpoke/issues'),
    )),
    license='MIT',
    author='Marcos Sanchez',
    author_email='marsanben92@gmail.com',
    maintainer='Marcos Sanchez',
    maintainer_email='marsanben92@gmail.com',
    description='WordPress information gathering tool',
    long_description='WordPress information gathering tool',  # TODO
    packages=['wpoke'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    python_requires='>=3.7',
    install_requires=install_requires,
    extras_require={
        'dev': [
            'pytest',
            'tox',
        ],
        'docs': [
        ]
    },
)
