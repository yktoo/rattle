#!/usr/bin/env python3

from setuptools import setup
from setuptools import find_packages

setup(
    name='rattle',
    description='Modular and lightweight ETL application',
    version='0.1.1.0',
    author='Dmitry Kann',
    url='https://github.com/yktoo/rattle',
    package_dir={'': 'pkg'},
    packages=find_packages('pkg'),
    package_data={
        '': ['*.json'],
    },
    install_requires=[],
    scripts=['app/rattle']
)
