# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='turtlesvg',
    version='3.1b',
    author='SATOH Naotaka',
    py_modules=['turtlesvg'],
    packages=['svgutl', 'dummyturtle'],
    package_dir={'':'turtlesvg'}
    )
