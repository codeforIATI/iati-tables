from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install

install_requires = [
    'lxml',
    'xmlschema',
    'sqlalchemy',
    'psycopg2-binary',
    'click',
    'boto3',
    'iatikit'
]

setup(
    name="iatidata",
    version="0.1",
    author="Open Data Services",
    author_email="code@opendataservices.coop",
    py_modules=["iatidata"],
    url="https://github.com/OpenDataServices/iatidata",
    license="MIT",
    description="Flatten the Iatis",
    install_requires=install_requires,
)
