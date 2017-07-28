"""Based on https://github.com/pypa/sampleproject/blob/master/setup.py"""

from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open                      # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='interface',
    version='0.1.0',
    description='Interfaces for Python',
    long_description=long_description,

    url='https://github.com/gwerbin/python_interface',
    author='Gregory Werbin',
    author_email='outthere@me.gregwerbin.com',

    license='Apache',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
    ],

    packages=find_packages(exclude=['docs', 'tests']),

    #install_requires=[],

    #extras_require={
    #    'dev': [],
    #    'test': [],
    #},
)
