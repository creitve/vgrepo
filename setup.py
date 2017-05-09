#!/usr/bin/env python
import sys
from setuptools import setup, find_packages

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(
    name='vgrepo',
    version='1.1.0',
    description='Utility for managing Vagrant repositories',
    long_description="""
        Pythonic tool for adding, listing and removing Vagrant images from repositories.
    """,
    author='Gleb Goncharov',
    author_email='gongled@gongled.ru',
    install_requires=['clint>=0.5.0'],
    url='https://github.com/gongled/vgrepo',
    package_dir={'': 'lib'},
    packages=find_packages('lib'),
    license='MIT',
    platforms='Posix; MacOS X; Windows',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    scripts=[
        'bin/vgrepo'
    ],
    **extra
)
