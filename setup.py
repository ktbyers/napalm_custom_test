from setuptools import setup
import os
import re


def find_version(*file_paths):
    """
    This pattern was modeled on a method from the Python Packaging User Guide:
        https://packaging.python.org/en/latest/single_source_version.html

    We read instead of importing so we don't get import errors if our code
    imports from dependencies listed in install_requires.
    """
    base_module_file = os.path.join(*file_paths)
    with open(base_module_file) as f:
        base_module_data = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              base_module_data, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='napalm_custom_test',
    version='0.0.1',
    description='Test NAPALM configuration operations',
    url='https://github.com/ktbyers/napalm_custom_test',
    author='Kirk Byers',
    author_email='ktbyers@twb-tech.com',
    license='Apache2',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=['napalm_custom_test',]
    install_requires=[
            'napalm>=2.0.0',
            'pytest',
            'tox'
    ],
)
