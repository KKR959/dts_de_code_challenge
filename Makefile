# Makefile for setup, test, and run
# Note: Commands are set to work on Windows Machines

.PHONY: all clean_venv init run test purge

# Clean: remove venv and pycache files
clean_venv:
	@echo Cleaning virtual environment...
	@if exist venv rmdir /S /Q venv
	@echo Cleanup finished.

# Purge: removes all log files and the db
purge:
	@echo Purging logs and database...
	@if exist logs rmdir /F /Q logs
	@if exist ro.db del /F /Q ro.db
	@echo Purge complete.

# Init: create virtual environment and install dependencies
init: clean_venv
	@echo Setting up virtual environment...
	python -m venv venv
	call venv\Scripts\activate && pip install -r requirements.txt
	@echo Virtual environment setup complete.

# Run: run main
run:
	@echo Running main program...
	@call venv\Scripts\activate && python main.py

# Test: run unit tests
test:
	@echo Running unit tests...
	@call venv\Scripts\activate && python unit_test.py
	@echo Unit tests complete.

# All: run clean_venv, init, test, and run
all: clean_venv init test run
	@echo All tasks complete.
