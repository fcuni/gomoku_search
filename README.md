# Generic Template

This is a generic template for a repository. It is intended to be used as a starting 
point for creating new repositories. It contains a number of files that are common to
most repositories, such as a README, LICENSE, and a pyproject file.

## Usage

To use this template, click the "Use this template" button at the top of the page.

## Installation

### Linux

It is convenient to make use of `pipx` to install general helper packages:

```bash
python -m venv $HOME/.venvs
source $HOME/.venvs/bin/activate
pip install pipx
pipx install black
pipx install isort
pipx install ruff
pipx install pre-commit
```

Use the Makefile to install the repo and its dependencies:

```bash
make setup
```
