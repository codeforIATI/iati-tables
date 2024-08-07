# IATI Tables

## Documentation

https://iati-tables.readthedocs.io/en/latest/

## Installation

### Backend Python code (batch job)

```
git clone https://github.com/codeforIATI/iati-tables.git
cd iati-tables
python3 -m venv .ve
source .ve/bin/activate
pip install -r requirements_dev.txt
```

Install postgres, sqlite and zip. e.g. on Ubuntu:

```
sudo apt install postgresql sqlite3 zip
```

Create a iatitables user and database:

```
sudo -u postgres psql -c "create user iatitables with password 'PASSWORD_CHANGEME'"
sudo -u postgres psql -c "create database iatitables encoding utf8 owner iatitables"
```

Run the code:

```
export DATABASE_URL="postgresql://iatitables:PASSWORD_CHANGEME@localhost/iatitables"
export IATI_TABLES_S3_DESTINATION=-
export IATI_TABLES_SCHEMA=iati
python -c 'import iatidata; iatidata.run_all(processes=6, sample=50)'
```

Run with refresh=False to avoid fetching all the data every time it's run. This
is very useful for quicker debugging.

```
python -c 'import iatidata; iatidata.run_all(processes=6, sample=50, refresh=False)'
```

`processes` is the number of processes spawned, and `sample` is the number of
publishers data processed. A sample size of 50 is pretty quick and generally
works. Smaller sample sizes, e.g. 1 fail because not all tables get created,
see https://github.com/codeforIATI/iati-tables/issues/10

Running the tests:

```
python -m pytest iatidata/
```

Linting:

```
isort iatidata/
black iatidata/
flake8 iatidata/
mypy iatidata/
```

### Web front-end

Install Node JS 20. e.g. on Ubuntu:

```
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs
```

Install yarn:

```
sudo npm install -g yarn
```

Install dependencies:

```
cd site
yarn install
```

Start the development server:

```
yarn serve
```

Build and view the site:

```
yarn build
cd site/dist
python3 -m http.server --bind 127.0.0.1 8000
```

### Docs

For live preview while writing docs, run the following command and go to http://127.0.0.1:8000

```
sphinx-autobuild docs docs/_build/html
```

## Update requirements

```
pip install pip-tools
pip-compile --upgrade
pip-sync requirements.txt
```
