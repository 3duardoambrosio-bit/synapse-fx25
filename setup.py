from setuptools import setup, find_packages

setup(
    name="fx25",
    version="2.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "numpy",
        "pandas",
    ],
)
