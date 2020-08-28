#!/usr/bin/env python

import sys
from setuptools import setup

install_requires = [
    'csvkit>=1.0.5',
    'agate>=1.6.1',
    'regex>=2020.7.14',
    # 'agate-excel>=0.2.2',
    # 'agate-dbf>=0.2.0',
    # 'agate-sql>=0.5.3',
    # 'six>=1.6.1'
]

if sys.version_info < (2, 7):
    install_requires.append('argparse>=1.2.1')
    install_requires.append('ordereddict>=1.1')
    install_requires.append('simplejson>=3.6.3')

setup(
    name='csvkitcat',
    version='1.5.0-alpha',
    description='The unofficial extended, awkward family of csvkit',
    long_description=open('README.rst').read(),
    author='Dan Nguyen',
    author_email='dansonguyen@gmail.com',
    url='https://github.com/dannguyen/csvkitcat',
    project_urls={
        'Documentation': 'https://csvkit.readthedocs.io/en/latest/',
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
        'Programming Language :: Python :: 3.5',
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
            'csvchart = csvkitcat.moreutils.csvchart:launch_new_instance',
            'csvcount = csvkitcat.moreutils.csvcount:launch_new_instance',
            'csvflatten = csvkitcat.moreutils.csvflatten:launch_new_instance',
            'csvgroupby = csvkitcat.moreutils.csvgroupby:launch_new_instance',
            'csvnorm = csvkitcat.moreutils.csvnorm:launch_new_instance',
            'csvpivot = csvkitcat.moreutils.csvpivot:launch_new_instance',
            'csvsed = csvkitcat.moreutils.csvsed:launch_new_instance',
            'csvslice = csvkitcat.moreutils.csvslice:launch_new_instance',
            'csvxcap = csvkitcat.moreutils.csvxcap:launch_new_instance',
            'csvxfind = csvkitcat.moreutils.csvxfind:launch_new_instance',
            'csvxplit = csvkitcat.moreutils.csvxplit:launch_new_instance',
        ]
    },
    install_requires=install_requires
)
