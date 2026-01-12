"""
Setup script for TCDB Domain Visualization.

This script installs the refactored TCDB Domain Visualization package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="tcdb-domain-visualization",
    version="2.0.0",
    author="Xiangyu(Leo) Shi",
    author_email="xiangy.shi@gmail.com",
    description="A comprehensive Python tool for analyzing protein domain architectures from TCDB proteins",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/xiangyshi/TCDB-Domain-Visualization",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "tcdb-visualize=src.cli.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt"],
    },
    keywords="bioinformatics, protein, domain, TCDB, visualization",
    project_urls={
        "Source": "https://github.com/xiangyshi/TCDB-Domain-Visualization",
        "Documentation": "https://github.com/xiangyshi/TCDB-Domain-Visualization/blob/main/README.md",
    },
) 