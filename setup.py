from ast import literal_eval
from setuptools import setup


DIR_SRC = 'uniseg'
VERSION = literal_eval(open(DIR_SRC+'/version.py').read())


setup(
    name = 'uniseg',
    version = VERSION,
    author = 'Masaaki Shibata',
    author_email = 'mshibata@emptypage.jp',
    url = 'https://bitbucket.org/emptypage/uniseg-python',
    description = 'Determine Unicode text segmentations',
    long_description = open('README.rst').read(),
    license = 'MIT',
    packages = ['uniseg'],
    package_data = {
        'uniseg': ['docs/*.html', 'samples/*.py']
    },
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Text Processing',
    ],
    zip_safe = False,
)
