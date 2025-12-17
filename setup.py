"""Setup script for paper2repo package."""
from setuptools import setup, find_packages
import os

# Read version from VERSION file
version_file = os.path.join(os.path.dirname(__file__), "VERSION")
with open(version_file, "r") as f:
    version = f.read().strip()

setup(
    name="paper2repo",
    version=version,
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
)
