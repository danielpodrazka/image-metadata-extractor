from setuptools import find_packages, setup

setup(
    name="image_metadata_extractor",
    version="0.1",
    packages=find_packages(exclude=["tests", "data"]),
)
