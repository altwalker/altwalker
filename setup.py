from setuptools import setup, find_packages

from altwalker.__version__ import VERSION


NAME = 'altwalker'
DESCRIPTION = 'AltWalker is an open source Model-Based Testing framework that supports running tests written in python3 and .NET/C#. You design your tests as a directed graph and AltWalker generates test cases from your graph (using GraphWalker) and executes them.'
URL = 'https://gitlab.com/altom/altwalker/altwalker/'
EMAIL = 'altwalker@altom.com'
AUTHOR = 'Altom Consulting'
REQUIRES_PYTHON = '>=3.4.0'
LICENSE = 'GNU GPLv3'


with open('requirements.txt') as f:
    REQUIRED = f.read().splitlines()


with open('README.md') as f:
    README = f.read()


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=README,
    long_description_content_type='text/markdown',
    license=LICENSE,
    url=URL,
    project_urls={
        "Bug Tracker": "https://gitlab.com/altom/altwalker/altwalker/issues?label_name=Bug",
        "Documentation": "https://altom.gitlab.io/altwalker/altwalker/",
        "Source": "https://gitlab.com/altom/altwalker/altwalker/",
    },

    author=AUTHOR,
    author_email=EMAIL,

    python_requires=REQUIRES_PYTHON,
    setup_requires=REQUIRED,
    install_requires=REQUIRED,
    packages=find_packages(exclude=['tests']),
    entry_points='''
        [console_scripts]
        altwalker=altwalker.cli:cli
    ''',

    classifiers=[
        "Development Status :: 4 - Beta",
        "Development Status :: 5 - Production/Stable",

        "Intended Audience :: Developers",
        "Intended Audience :: Other Audience",

        "Environment :: Console",

        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",

        "Programming Language :: C#",
        "Programming Language :: Cython",
        "Programming Language :: Python :: Implementation",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",

        "Operating System :: OS Independent",

        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Testing :: Acceptance",
    ],
    keywords="model-based-testing testing tests",
)
