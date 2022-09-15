# RAPP GUI Package

The **responsible academic performance prediction** (RAPP) GUI is a tool to train, save, load and evaluate Machine Learning models.

## How it internally works

1. Loads SQLite database.
2. SQL query on database to obtain a new database.
3. One column of the new database is the target label. The rest are training data. The last column is by default the target.
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

We provide a dummy database `data/rapp_dummy.db` that is compatible with the tool.
The dummy database consists of artificial data that do not represent any real student.
The SQLite database is to be positioned in the `data/` directory:

```tree
data/rapp.db
```

SQL Templates already available are compatible with the database. The templates are located in the `sqltemplates/` directory:

```tree
sqltemplates/
```

### First start

The GUI can be started by executing

```bash
python -m rapp.gui
```

For a headless run, settings are provided. To run an example evaluation, simply execute

```bash
python -m rapp --config-file settings/GUI/cs/first_term_ects/cs_first_term_ects_3_dropout.ini
```

The reports are saved under `reports/`


### Explainable AI (Decision Tree)

Example configuration files for the explainability modules are located in `settings/explain/`. To run the prediction and get xAI results, execute

```bash
python -m rapp.explain --config-file settings/explain/CSDropout.ini
``
