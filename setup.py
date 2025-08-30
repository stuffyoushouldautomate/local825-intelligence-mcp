#!/usr/bin/env python3
"""
Setup script for Local 825 Intelligence MCP Server
"""

from setuptools import setup, find_packages

setup(
    name="local825-intelligence-mcp",
    version="1.0.0",
    description="Local 825 Intelligence MCP Server - High-performance intelligence data server",
    author="Jeremy Harris",
    author_email="jeremy@augments.art",
    packages=find_packages(),
    install_requires=[
        "flask>=3.0.0",
        "mysql-connector-python>=9.4.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
        "lxml>=4.9.3",
        "feedparser>=6.0.10",
        "openai>=1.3.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "local825-mcp=app:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
