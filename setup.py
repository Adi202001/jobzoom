#!/usr/bin/env python3
"""Setup script for JobCopilot"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jobcopilot",
    version="0.1.0",
    author="JobCopilot Team",
    author_email="team@jobcopilot.dev",
    description="Multi-Agent Job Application Automation System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jobcopilot/jobcopilot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.9",
    install_requires=[
        # Core dependencies (minimal for now)
    ],
    extras_require={
        "full": [
            "requests>=2.28.0",
            "beautifulsoup4>=4.11.0",
            "lxml>=4.9.0",
            "pdfplumber>=0.7.0",
            "python-docx>=0.8.11",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "jobcopilot=src.cli:main",
        ],
    },
)
