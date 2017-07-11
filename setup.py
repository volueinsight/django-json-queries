import os
from setuptools import find_packages, setup

version = '0.0.1'

# Helper to read and convert the Markdown readme file to reStructuredText as is
# expected by pypi.
# Taken from this answer on Stack Overflow: https://stackoverflow.com/a/23265673
try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

# Read the readme file
README = read_md('README.md')

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-json-queries',
    version=version,
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    license='MIT License',
    description='A Django app for processing complex model queries from JSON.',
    long_description=README,
    url='https://github.com/mkonline/django-json-queries/',
    author='Sigurd Ljødal',
    author_email='slj@mkonline.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
