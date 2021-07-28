# RAPP Prediction Package

Responsible Academic Performance Prediction (RAPP)

## How it internally works

1. Loads `superx` database.
2. SQL query on `superx` database to obtain a new database.
3. One column of the new database is the target label. The rest are training data.
4. With a given list of categorical columns, those are then one-hot encoded.
5. With the predefined type of the supervised learning task, respective supervised learning algorithms are used. The data is ran through a Machine Learning Pipeline.

## Developer Setup

### Requirements

Ensure you work on a virtual environment and install the dependencies.

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### Required Files

The `superx` database is to be positioned in the `data` directory:

```tree
data/rapp.db
```

The SQL files are to be positioned in the `sql` directory:

```tree
sql/CSFirstSemester.sql
```

### First start

A config file `config.ini` is already available and contains the required arguments to run the prediction. To run the prediction, simply execute

```bash
python src/main.py --config-file settings/config.ini
```
