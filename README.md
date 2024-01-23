# IATI Tables

## Installation

```
git clone https://github.com/codeforIATI/iati-tables.git
cd iati-tables
python3 -m venv .ve
source .ve/bin/activate
pip install -r requirements.txt
```

## Update requirements

```
pip install pip-tools
pip-compile --upgrade
pip-sync requirements.txt
```
