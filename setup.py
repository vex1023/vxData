from __future__ import print_function

import os
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

import vxData as source_packages

here = os.path.abspath(os.path.dirname(__file__))

# 包名称
name = 'vxData'
# 版本号从源代码包里获取
version = source_packages.__version__
# 项目首页
home_pages = 'http://github.com/'
# 作者相关信息
author = source_packages.__author__
author_email = source_packages.__authoremail__
# 项目简介
description = '一句话的项目介绍'
# 测试用例
test_suite = 'demo.tests.test_demo'
# 项目分类
classifiers = [
    'Programming Language :: Python3.4',
    'Programming Language :: Python3.5',
    'Development Status :: 4 - Beta',
    'Natural Language :: Chinese',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: The MIT License (MIT)',
    'Operating System :: OS Independent',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

requirements = []

readme = None
long_description = ''

if os.path.exists('README.rst'):
    readme = 'README.rst'
elif os.path.exists('README.md'):
    readme = 'README.md'
if readme:
    with open(readme, 'rb') as f:
        long_description = f.read().decode('utf-8')


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(
    name=name,
    version=version,
    url=home_pages,
    license='The MIT License (MIT)',
    author=author,
    tests_require=['pytest'],
    install_requires=requirements,
    cmdclass={'test': PyTest},
    author_email=author_email,
    description=description,
    long_description=long_description,
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    test_suite=test_suite,
    classifiers=classifiers,
    extras_require={
        'testing': ['pytest'],
    }
)
