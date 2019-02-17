#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-cov-threshold',
    version='0.1.0',
    author='Dima Kruk',
    author_email='krkdima@gmail.com',
    maintainer='Dima Kruk',
    maintainer_email='krkdima@gmail.com',
    license='MIT',
    url='https://github.com/krkd/pytest-cov-threshold',
    description='Pytest plugin that allows to define coverage threshold for a module/packet',
    long_description=read('README.rst'),
    py_modules=['pytest_cov_threshold'],
    python_requires='>=3.4',
    install_requires=['pytest>=3.5.0'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'cov-threshold = pytest_cov_threshold',
        ],
    },
)
