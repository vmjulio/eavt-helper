"""Package setup"""
import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Core dependencies - keep versions flexible for better compatibility
requirements = [
    "click>=8.0.0,<9.0.0",
    "pandas>=1.3.0,<3.0.0",
    "numpy>=1.20.0,<2.0.0",
    "python-dateutil>=2.8.0",
    "pytz>=2021.0",
]

# Development dependencies
dev_requirements = [
    "pytest>=6.0.0",
    "pytest-cov>=2.0.0",
    "black>=21.0.0",
    "flake8>=3.8.0",
]

setuptools.setup(
    name="eavt-helper",
    version="0.2.0",
    author="Vitor Julio",
    author_email="",
    description="CLI tool to convert snapshots to EAVT logs and EAVT logs to Slowly Changing Dimensions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=["dist", "build", "*.egg-info", "tests"]),
    url="https://github.com/vmjulio/eavt-helper",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
    },
    entry_points={"console_scripts": ["eavt-helper = eavt_helper.main:cli"]},
)
