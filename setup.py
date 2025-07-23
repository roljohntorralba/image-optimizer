#!/usr/bin/env python3
"""
Setup script for Rol's Image Optimizer
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="rols-image-optimizer",
    version="1.0.0",
    author="Rol John Torralba",
    author_email="roljohntorralba@example.com",
    description="A GUI application for optimizing images to WEBP and AVIF formats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/roljohntorralba/image-optimizer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pillow>=10.0.0",
        "pillow-avif-plugin>=1.4.0",
    ],
    extras_require={
        "dev": [
            "pyinstaller>=6.0.0",
            "setuptools>=65.0.0",
            "wheel>=0.38.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "rols-image-optimizer=image_optimizer:main",
        ],
        "gui_scripts": [
            "rols-image-optimizer-gui=image_optimizer:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.py"],
    },
)
