#!/usr/bin/env python
#:coding=utf-8:

from setuptools import setup, find_packages
 
setup (
    name='django-newauth',
    version='0.31',
    description='Authentication for Django done right',
    author='Ian Lewis',
    author_email='ianmlewis@gmail.com',
    url='https://bitbucket.org/IanLewis/django-newauth/',
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Environment :: Plugins',
      'Framework :: Django',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Programming Language :: Python',
      'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    include_package_data=True,
    packages=find_packages(),
    test_suite='tests.main',
    zip_safe=False,
)
