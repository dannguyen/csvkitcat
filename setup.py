#!/usr/bin/env python

import os
import sys
from setuptools import setup

HERE_PATH = os.path.abspath(os.path.dirname(__file__))
ABOUT = {}
with open(os.path.join(HERE_PATH, "csvkitcat", "__about__.py"), "r") as f:
    exec(f.read(), ABOUT)

with open("README.rst", "r") as f:
    README = f.read()

install_requires = [
    'csvkit>=1.0.5',
    "altair>=4.1",
    "altair-viewer>=0.3.0",
    "python-slugify>=4.0",
    'regex>=2020.7.14',
]

dev_requires = [
    'coverage>=4.4.2',
    'nose>=1.1.2',
    'sphinx>=1.0.7',
    'sphinx_rtd_theme',
    'tox>=3.1.0',
]


setup(
    name=ABOUT["__title__"],
    version=ABOUT["__version__"],
    description=ABOUT["__description__"],
    author=ABOUT["__author__"],
    author_email=ABOUT["__author_email__"],
    url=ABOUT["__url__"],
    long_description=README,
    long_description_content_type="text/x-rst",
    project_urls={
        'Documentation': 'https://csvkitcat.readthedocs.io/en/latest/',
    },
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    packages=[
        'csvkitcat',
    ],
    entry_points={
        'console_scripts': [
            'csvcount = csvkitcat.moreutils.csvcount:launch_new_instance',
            'csvflatten = csvkitcat.moreutils.csvflatten:launch_new_instance',
            'csvgroupby = csvkitcat.moreutils.csvgroupby:launch_new_instance',
            'csvnorm = csvkitcat.moreutils.csvnorm:launch_new_instance',
            'csvpivot = csvkitcat.moreutils.csvpivot:launch_new_instance',
            'csvrgrep = csvkitcat.moreutils.csvrgrep:launch_new_instance',
            'csvsed = csvkitcat.moreutils.csvsed:launch_new_instance',
            'csvslice = csvkitcat.moreutils.csvslice:launch_new_instance',
            'csvwhere = csvkitcat.moreutils.csvwhere:launch_new_instance',
            'csvxcap = csvkitcat.moreutils.csvxcap:launch_new_instance',
            'csvxfind = csvkitcat.moreutils.csvxfind:launch_new_instance',
            'csvxplit = csvkitcat.moreutils.csvxplit:launch_new_instance',
        ]
    },
    install_requires=install_requires,
    extras_require={
        'dev': dev_requires
    }
)
