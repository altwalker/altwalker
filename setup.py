from setuptools import setup, find_packages

from altwalker.__version__ import VERSION


NAME = 'altwalker'
DESCRIPTION = """Altwalker is an open source, Model-based testing framework for automating
your test execution. You design your tests as a directional graph and altwalker executes
them. It relies on Graphwalker to generate paths through your tests graph."""
URL = 'https://gitlab.com/altom/altwalker/altwalker'
EMAIL = ''
AUTHOR = 'Altom Consulting'
REQUIRES_PYTHON = '>=3.4.0'

with open('requirements.txt') as f:
    required = f.read()
    REQUIRED = required.split("\n")

with open('README.md') as f:
    README = f.read()

with open('LICENSE') as f:
    LICENSE = f.read()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=README,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    license=LICENSE,
    packages=find_packages(),
    install_requires=REQUIRED,
    entry_points='''
        [console_scripts]
        altwalker=altwalker.cli:cli
    ''',
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Testing",
        "Development Status :: 4 - Beta",
    ],
)
