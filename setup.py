import setuptools
import glob
import os

with open("README.rst", "r") as fh:
    long_description = fh.read()

datafiles = []

setuptools.setup(
    name="pyavtools",
    version="0.1.0",
    author="Garrett Herschleb",
    author_email="9.planetary.drive@gmail.com",
    description="pyAvTools",
    long_description=long_description,
    #long_description_content_type="text/x-rst",
    url="https://github.com/makerplane/pyAvDb",
    packages=setuptools.find_packages(exclude=["tests.*", "tests"]),
    install_requires = ['pyyaml',],
    #data_files = datafiles,
    entry_points = {
        'console_scripts': ['makecifpindex=pyavtools.utils.MakeCIFPIndex:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)"
        "Operating System :: POSIX :: Linux",
    ],
    test_suite = 'tests',
)
