from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
name = "joltos"
exec(open('joltos/version.py').read())


# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=name,
    version=__version__,
    description='OS Image Builder',
    long_description=long_description,
    url="https://github.com/srand/joltos",
    author="Robert Andersson",
    author_email="srand@github.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
    ],
    keywords=[
        "alpine",
        "debian",
    ],
    package_data={
        "joltos": ["templates/*"],
    },
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=["jolt"],
    dependency_links=[],
)
