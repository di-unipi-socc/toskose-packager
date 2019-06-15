from setuptools import setup, find_packages
import app


test_require = [
    'pytest',
    'mock',
    "pytest-cov==2.7.1",
    'coverage==4.5.3',
    'codacy-coverage==1.3.11',
]

install_requires = [
    'tosca-parser==1.4.0',
    'termcolor==1.1.0',
    'pyfiglet==0.8.post1',
    'six==1.12.0',
    'colorama==0.4.1',
    'setuptools==41.0.0',
    'click==7.0',
    'docker==3.7.2',
    'ruamel.yaml==0.15.94',
    'jsonschema==3.0.1',
]


setup(
    name=app.__name__,
    version=app.__version__,
    description=app.__doc__.strip(),
    long_description="",
    keywords="toskose docker docker-compose tosca",
    url="https://github.com/matteobogo/toskose",
    author=app.__author__,
    author_email=app.__email__,
    license=app.__license__,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'toskose = app.__main__:main',
        ],
    },
    #extras_require=[],
    install_requires=install_requires,
    tests_require=test_require,
)