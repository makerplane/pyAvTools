import setuptools
import glob
import os

with open("README.rst", "r") as fh:
    long_description = fh.read()

datafiles = []

setuptools.setup(
    name="pyavdb",
    version="0.1.0",
    author="Garrett Herschleb",
    author_email="9.planetary.drive@gmail.com",
    description="pyAvDb ",
    long_description=long_description,
    #long_description_content_type="text/x-rst",
    url="https://github.com/makerplane/pyAvDb",
    packages=setuptools.find_packages(),
    install_requires = ['pyyaml',],
    data_files = datafiles,
    #test_suite = 'tests',
    #scripts = ['bin/fixgw', 'bin/fixgwc'],
    # entry_points = {
    #     'console_scripts': ['fixgw=fixgw.server:main', 'fixgwc=fixgw.client:main'],
    # },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)"
        "Operating System :: POSIX :: Linux",
    ],
    test_suite = 'tests',
)
