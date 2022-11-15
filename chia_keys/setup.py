#!/usr/bin/env python

from setuptools import setup

setup(
    name = "chia keys",
    version = "1.1.0",
    python_requires=">=3.7",
    author = "Ardika Rommy Sanjaya",
    author_email="contact@ardikars.com",
    packages=[
        "chia_keys",
        "chia_keys.consensus",
        "chia_keys.types",
        "chia_keys.types.blockchain_format",
        "chia_keys.util",
        "chia_keys.wallet",
        "chia_keys.wallet.puzzles",
    ],
    entry_points={
        "console_scripts": ["chia_keys = chia_keys.chia_keys:main"],
    },
    setup_requires=["setuptools_scm"],
    include_package_data=True,
    install_requires=[
    	"bitstring==3.1.9",
        "blspy==1.0.16",
        "chia_rs==0.1.14",
        "click==8.1.3",
        "clvm==0.9.7",
        "clvm-tools==0.4.6",
        "clvm_rs==0.1.24",
        "clvm_tools_rs==0.1.25",
        "filelock==3.8.0",
        "typing_extensions==4.4.0",
    ],
    package_data={
        "": ["*.clvm", "*.clvm.hex", "*.clib", "*.clinc", "*.clsp", "py.typed"],
        "chia_keys.util": ["english.txt"],
    },
    url="https://github.com/ardikars/farm",
    license="https://opensource.org/licenses/Apache-2.0",
    description="Chia keys generator.",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Security :: Cryptography",
    ],
    project_urls={
        "Bug Reports": "https://github.com/ardikars/farm",
        "Source": "https://github.com/ardikars/farm",
    },
)
