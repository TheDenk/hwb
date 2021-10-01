# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        file_content = f.read()
    return file_content


def get_version():
    """Get version from the package without actually importing it."""
    init = read('hwb/__init__.py')
    for line in init.split('\n'):
        if line.startswith('__version__'):
            return eval(line.split('=')[1])


setup(
    name='hwb',
    version=get_version(),
    description='Hand written blot augmentation.',
    long_description=read('README.txt'),
    long_description_content_type='text/markdown',
    url='https://github.com/TheDenk/hwb',
    author='Karachev Denis',
    author_email='welcomedenk@gmail.com',
    license='MIT',
    install_requires=['bezier', 'opencv-python>=4.1.1'],
    packages=find_packages(),
)
