from setuptools import setup, find_packages

setup(
    name="seyaml",
    version="0.1.0",
    description="YAML loader with support for !secret, !env, and !enc tags",
    author="Your Name",
    author_email="you@example.com",
    packages=find_packages(),
    install_requires=[
        "PyYAML>=6.0",
        "cryptography>=40.0",
        "click>=8.0",
    ],
    entry_points={
        "console_scripts": [
            "seyaml=seyaml.cli:cli",
        ],
    },
    python_requires=">=3.7",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
