.EXPORT_ALL_VARIABLES:
.PHONY: venv install sync upgrade pre-commit check clean

GLOBAL_PYTHON=${python}
LOCAL_PYTHON=~/code/research/research-ml/.venv/bin/python
LOCAL_PIP_COMPILE=~/code/research/research-ml/.venv/bin/pip-compile
LOCAL_PIP_SYNC=~/code/research/research-ml/.venv/bin/pip-sync

venv: ${GLOBAL_PYTHON}
	@echo "Creating virtual environment..."
	- deactivate
	python -m venv .venv
	@echo "Virtual environment created."

install: $(LOCAL_PYTHON)
	@echo "Installing dependencies..."
	$(LOCAL_PYTHON) -m pip install --upgrade pip
	$(LOCAL_PYTHON) -m pip install pip-tools
	$(LOCAL_PIP_COMPILE) --output-file requirements.txt --resolver=backtracking --allow-unsafe
	$(LOCAL_PIP_COMPILE) --output-file requirements-dev.txt --resolver=backtracking --allow-unsafe --extra dev
	@echo "Dependencies installed. Syncing..."
	$(LOCAL_PIP_SYNC) requirements-dev.txt --pip-args="--no-cache-dir"
	@echo "Dependencies done syncing."

sync: $(LOCAL_PYTHON) $(LOCAL_PIP_SYNC)
	@echo "Syncing dependencies..."
	$(LOCAL_PYTHON) -m pip install --upgrade pip
	$(LOCAL_PIP_SYNC) requirements-dev.txt --pip-args="--no-cache-dir"
	@echo "Dependencies done syncing."

upgrade: $(LOCAL_PYTHON) $(LOCAL_PIP_COMPILE)
	@echo "Upgrading dependencies..."
	$(LOCAL_PYTHON) -m pip install --upgrade pip
	$(LOCAL_PIP_COMPILE) --upgrade --output-file requirements.txt --resolver=backtracking --allow-unsafe
	@echo "Dependencies upgraded."

pre-commit:
	@echo "Running pre-commit..."
	pre-commit install
	pre-commit autoupdate
	@echo "Pre-commit done."

setup: venv install pre-commit

check: $(LOCAL_PYTHON)
	@echo "Running checks..."
	ruff check --fix .
	isort .
	black .
	pydocstyle .
	@echo "Checks done."

clean:
	if exist .git/hooks (rmdir .git/hooks /q /s)
	- deactivate
	if exist .venv (rmdir /s /q .venv)
