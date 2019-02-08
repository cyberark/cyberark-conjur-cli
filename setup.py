#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name = "conjur-api-python3",
    version = "0.0.1",
    packages = find_packages(),
    zip_safe = True,

    install_requires = open('requirements.txt').readlines(),

    package_data = {
        '': ['*.md'],
    },

    author = "CyberArk Software, Inc",
    author_email = "CyberArk Maintainers <conj_maintainers@cyberark.com>",
    description = "APIs for interacting with the Conjur v5 appliance",
    license = "MIT",
    url = "https://github.com/conjurinc/conjur-api-python3",
    keywords = [
        "conjur",
        "cyberark",
        "security",
        "vault",
        "privileged access",
        "microservices"
    ],
    classifiers = [
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
