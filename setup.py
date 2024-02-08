from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name='VoxPoser',
    version='0.1',
    author='Yan Zhang', 
    author_email='',
    packages=find_packages(),
    long_description=open('README.md').read()
)