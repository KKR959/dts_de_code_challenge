# Makefile for setup, test, and run
# Note: Commands are set to work on Windows Machines

.PHONY: all clean init run test

# Clean: remove venv and pycache files
clean:
	@echo Cleaning environment...
	@if exist venv rmdir /S /Q venv
	# @if exist log.txt del /F /Q log.txt # NOTE to remove this line and replace with purge function of all logs
	@if exist ro.db del /F /Q ro.db
	@echo Cleanup finished.

# Init: create virtual environment and install dependencies
init: clean
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
	@call venv\Scripts\activate && python -m unittest discover -s tests -p "*_test.py"
	@echo Unit tests complete.

# All: run init, test, and run
all: clean init test run
	@echo All tasks complete.
