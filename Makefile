PYTHON ?= python

.PHONY: check
check:
	$(PYTHON) tools/fast_check.py
