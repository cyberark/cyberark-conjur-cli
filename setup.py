#!/usr/bin/env python3

"""
Setup.py

This module is used for installation of this code directly on the machine
"""

import os.path

from setuptools import setup, find_packages

PACKAGE_NAME = "conjur_api_python3"
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
VERSION_FILE = os.path.join(CURRENT_DIR, PACKAGE_NAME, "version.py")

VERSION_DATA = {}
with open(VERSION_FILE, 'r') as version_fp:
    exec(version_fp.read(), VERSION_DATA)

setup(
    name="conjur-api-python",
    version=VERSION_DATA['__version__'],
    packages=find_packages(),
    zip_safe=True,

    scripts=['bin/conjur-py3-cli'],

    entry_points = {
        'console_scripts': ['conjur-py3-cli=conjur_api_python3:Cli.launch'],

        'setuptools.installation': [
            'eggsecutable = conjur_api_python3:Cli.launch',
        ]
    },

    # Keep this in sync with requirements.txt
    install_requires=[
        "nose2>=0.8.0",
        "requests>=2.21.0",
        "PyYAML>=3.13",
    ],

    package_data={
        '': ['*.md'],
    },

    author="CyberArk Software, Inc",
    author_email="CyberArk Maintainers <conj_maintainers@cyberark.com>",
    description="APIs for interacting with the Conjur v5 appliance",
    license="MIT",
    url="https://github.com/conjurinc/conjur-api-python3",
    keywords=[
        "conjur",
        "cyberark",
        "security",
        "vault",
        "privileged access",
        "microservices"
        ],
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: Office/Business",
        "Topic :: Security",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
        "Topic :: Utilities",
        ],
)
