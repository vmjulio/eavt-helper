"""Package setup"""
import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

requirements = [
    "click==8.0.3",
    "numpy==1.22.0",
    "pandas==1.3.5",
    "python-dateutil==2.8.2",
    "pytz==2021.3",
    "six==1.16.0"
]

setuptools.setup(
    name="eavt-helper",
    version="0.1-beta",
    author="Vitor Julio",
    packages=setuptools.find_packages(exclude=["dist", "build", "*.egg-info", "tests"]),
    url="https://github.com/vmjulio/eavt-helper",
    install_requires=["click", "pandas"],
    entry_points={"console_scripts": ["eavt-helper = eavt_helper.main:cli"]},
)
