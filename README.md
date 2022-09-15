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

Optionally, if visualisation of decision trees or alike is needed,
make sure that [Graphviz](https://graphviz.org/download/) is installed on your
system.

### Required Files

The `superx` SQLite database is to be positioned in the `data` directory:

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
python -m rapp --config-file settings/pipeline/config.ini
```

To run the GUI, simply execute

```bash
python -m rapp.gui
```

### Explainable AI (Decision Tree)

Example configuration files for the explainability modules are located in `settings/explain/`. To run the prediction and get xAI results, execute

```bash
python -m rapp.explain --config-file settings/explain/CSDropout.ini
``
