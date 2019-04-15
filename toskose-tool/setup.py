from setuptools import setup, find_namespace_packages
import app


setup(
    name=app.__name__,
    version=app.__version__,
    packages=find_namespace_packages(),

    scripts=[],

    install_requires=[],

    package_data={},

    # metadata (PyPI)
    author="Me",
    author_email="matteo.bogo@protonmail.com",
    description="A tool for translating a TOSCA-based configuration into docker-compose.",
    license="GPL",
    keywords="toskose docker docker-compose tosca",
    url="https://github.com/matteobogo/toskose",

)