from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='encviewfuse',
    version='0.3.0.post1',
    description='A fuse implementation of an encrypted view on a given directory.',
    long_description=long_description,
    url='https://github.com/seiferma/encviewfuse',
    author='Stephan Seifermann',
    author_email='seiferma@t-online.de',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Filesystems',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: BSD :: FreeBSD',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only'
    ],
    keywords='encryption fuse view',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['fusepy', 'deterministic_encryption_utils'],
    entry_points={
        'console_scripts': [
            'encviewfuse_fs=encviewfuse.fuse.EncryptedFuseFs:main'
        ],
    },
)
