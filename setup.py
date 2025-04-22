from distutils.core import Extension

from setuptools import find_packages
from setuptools import setup

packages = [
    "attentionAnalyses",
]


# class get_pybind_include(object):
# def __init__(self, user=False):
# self.user = user

# def __iter__(self):
# for k in str(self):
# yield k

# def __str__(self):
# import pybind11
# return pybind11.get_include(self.user)

# radon_ext = Extension('fklab.radon.radonc',
# sources = ['fklab/radon/src/pybind_radon.cpp', 'fklab/radon/src/radon.cpp'],
# libraries = [],
# include_dirs = [get_pybind_include(), get_pybind_include(user=True)],
# language = "c++",
# extra_compile_args = ['-std=c++11', '-O3']
# )


import re

# VERSIONFILE = "fklab/version/_internal_version/_version.py"
# verstrline = open(VERSIONFILE, "rt").read()
# VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
# mo = re.search(VSRE, verstrline, re.M)
# if mo:
#     verstr = mo.group(1)
# else:
#     raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))


setup(
    name="project_attention",
    packages=packages,
    # ext_modules = [radon_ext,],
    # fklab-python-core is a non-pypi dependency
    # with which we will have to deal separately at some point
    # the dependencies of pymc3 are different
    # in the conda-forge and pypi packages
    # (because available versions are different)
    # which leads to `conda build` failing
    # so we leave pymc3 out for now
    # install_requires=['regex', 'theano', 'pymc3', 'networkx', 'seaborn', 'scikit-learn', 'scikit-image'],
    install_requires=[],
    entry_points={},
    author="Lies Deceuninck",
    author_email="Lies.deceuninck@nerf.be",
    description="Farrow Lab project Lies D.",
    zip_safe=False,
    include_package_data=True,
)
