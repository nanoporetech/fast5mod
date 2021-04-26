import os
import re
import sys
from glob import glob
import importlib.util
import shutil
from setuptools import setup, find_packages, Extension
from setuptools import Distribution, Command
from setuptools.command.install import install
from setuptools.command.build_ext import build_ext
import subprocess

__pkg_name__ = 'fast5mod'
__author__ = 'ont-research'
__description__ = 'Extraction of modified base data from Guppy Fast5 output'

# Use readme as long description and say its github-flavour markdown
from os import path
this_directory = path.abspath(path.dirname(__file__))
kwargs = {'encoding':'utf-8'} if sys.version_info.major == 3 else {}
with open(path.join(this_directory, 'README.md'), **kwargs) as f:
    __long_description__ = f.read()
__long_description_content_type__ = 'text/markdown'

__path__ = os.path.dirname(__file__)
__pkg_path__ = os.path.join(os.path.join(__path__, __pkg_name__))

# find version
verstrline = open(os.path.join(__pkg_name__, '__init__.py'), 'r').read()
vsre = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(vsre, verstrline, re.M)
if mo:
    __version__ = mo.group(1)
else:
    raise RuntimeError('Unable to find version string in "{}/__init__.py".'.format(__pkg_name__))

# create requirements from requirements.txt
dir_path = os.path.dirname(__file__)
install_requires = []
with open(os.path.join(dir_path, 'requirements.txt')) as fh:
    reqs = (
        r.split('#')[0].strip()
        for r in fh.read().splitlines() if not r.strip().startswith('#')
    )
    for req in reqs:
        if req.startswith('git+https'):
            req = req.split('/')[-1].split('@')[0]
        install_requires.append(req)


if __name__ == '__main__':

    pymajor, pyminor = sys.version_info[0:2]
    if (pymajor < 3) or (pyminor not in {5, 6, 7, 8}):
        raise RuntimeError(
            '`{}` is unsupported on your version of python, '
            'please use python 3.5 or python 3.6.'.format(__pkg_name__))

    setup(
        name=__pkg_name__,
        version=__version__,
        url='https://github.com/nanoporetech/{}'.format(__pkg_name__),
        author=__author__,
        description=__description__,
        long_description=__long_description__,
        long_description_content_type=__long_description_content_type__,
        python_requires='>=3.5.*,<3.9',
        packages=find_packages(exclude=['*.test', '*.test.*', 'test.*', 'test']),
        package_data={},
        cffi_modules=["build.py:ffibuilder"],
        install_requires=install_requires,
        data_files=[],
        entry_points = {
            'console_scripts': [
                '{0} = {0}.{0}:main'.format(__pkg_name__),
            ]
        },
        scripts=[],
        zip_safe=False,
        cmdclass={},
    )
