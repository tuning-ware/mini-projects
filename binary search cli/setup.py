from setuptools import setup, find_packages

setup(
    name="algoz",
    version="1.0.0",
    # recursively search our project directory for packages (folders containing __init__.py files)
    packages=find_packages(),
    # algoz should call main function in app.py file
    entry_points={"console_scripts": ["algoz=algoz.app:main"]},
)