#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = "Chia Keys",
    version = "1.1.0",
    python_requires=">=3.7",
    author = "Ardika Rommy Sanjaya",
    author_email="contact@ardikars.com",
    packages=find_packages(exclude = ("tests",)),
    entry_points={
        "console_scripts": ["chia_keys = chia_keys.chia_keys:main"],
    },
    setup_requires=["setuptools_scm"],
    include_package_data=True,
    install_requires=[
    	"chia-blockchain==1.4.0",
    ],
    package_data={
        "": ["*.clvm", "*.clvm.hex", "*.clib", "*.clsp", "*.clsp.hex", "*.txt"],
    },
    url="https://github.com/ardikars/farming-tools",
    license="https://opensource.org/licenses/Apache-2.0",
    description="Chia keys generator.",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Security :: Cryptography",
    ],
    project_urls={
        "Bug Reports": "https://github.com/ardikars/farming-tools",
        "Source": "https://github.com/ardikars/farming-tools",
    },
)
