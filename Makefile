################################
#    Makefile for pyavtools    #
################################
SHELL := /bin/bash


##################################### I N I T   T A R G E T S #####################################
venv:
	python3 -m venv venv
.PHONY: venv

init.marker: setup.py
	pip install -e .[install]
	touch init.marker
init: init.marker
.PHONY: init