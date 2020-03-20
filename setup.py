from setuptools import setup, find_packages
import os
import codecs
from os.path import join

project_root = os.path.dirname(os.path.abspath(__file__))


version = {}
with open(join(project_root, 'stockmanager/version.py')) as read_file:
    exec(read_file.read(), version)

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

with open(join(project_root, 'requirements.txt')) as read_file:
    REQUIRED = read_file.read().splitlines()

setup(
    name='stockmanager',
    version='0.0.2',
    description='Stock Manager',
    long_description=LONG_DESCRIPTION,
    # py_modules=['stockmanager'], 
    # packages=find_packages(exclude=["tests"]),
    # packages=['src'],
    package_dir={'': 'stockmanager'},
    # packages=find_packages(where='src'),
    install_requires=REQUIRED,
    author='Jiajun Yang',
    author_email='thejyang@gmail.com',
)
