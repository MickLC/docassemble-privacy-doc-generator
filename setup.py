import os
import sys
from setuptools import setup, find_packages

setup(
    name='docassemble-privacy-doc-generator',
    version='0.1.0',
    description='A Docassemble package for generating GDPR-compliant privacy policy documents',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/MickLC/docassemble-privacy-doc-generator',
    author='MickLC',
    author_email='',
    license='AGPL-3.0',
    packages=find_packages(),
    namespace_packages=['docassemble'],
    install_requires=[
        'docassemble.base',
    ],
    zip_safe=False,
    package_data={
        'docassemble.privacydocgenerator': [
            'data/questions/*.yml',
            'data/questions/includes/*.yml',
            'data/templates/*',
            'data/sources/*',
            'data/static/css/*',
            'data/static/js/*',
        ]
    },
)
