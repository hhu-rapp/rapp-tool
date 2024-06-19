# RAPP GUI Package (MLOps for Deploying Responsible Machine Learning Models)

The **responsible academic performance prediction** (RAPP) GUI is an **MLOps application**
to **train, save, load** and **evaluate Machine Learning models** on **any SQLite database**. Users can load a database or a `.csv` file, query custom SQL queries and use the resulting database as training/test data for the implemented Machine Learning pipeline.

For the specific use case of predicting students' performance data from the Heinrich Heine University, this package provides SQL templates that leverages the complexity of feature engineering away from the user.

## Tutorial

1. Load SQLite database or `.csv` file.
2. Optional: Query with SQL to obtain the training and test data.
3. Select a column as the target label. By default, the last column is set as the target variable.
All other columns are used as input features.
4. Select all categorical columns that need to be one-hot encoded.
5. Select supervised learning task: Classification/Regression
6. Select machine learning models to train on the data.
7. Click `Train` to start the training.

## Installation

### Cloning the Repository

Make sure you have installed `git lfs` in your system to correctly clone `data/rapp_dummy.db`.

Clone the repository:
```bash
git clone https://github.com/hhu-rapp/rapp-tool.git
```

Calculate the sha265 checksum of `data/rapp_dummy.db` (UNIX-like systems):
```bash
sha256sum data/rapp_dummy.db
```

The checksum of the dummy database `data/rapp_dummy.db` should be:
`d5aac60436d931174f2b02ea32c87c7d32f442021022380e8af376b3d817ee69`

### Setup Environments (2 Options)

Setup [virtual environment](https://docs.python.org/3/library/venv.html) with Python==3.8
and install the dependencies.

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

**OR**

Using conda (anaconda/miniconda):

```bash
conda create -n "rapp-tool" python=3.8
conda activate rapp-tool
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

SQL Templates are already available and are compatible with the database. The templates are located in the `sqltemplates/` directory:

```tree
sqltemplates/
```

## First start

The GUI can be started by executing (for Python's virtual environment):

```bash
source env/bin/activate
python -m rapp.gui
```

For conda environment:

```bash
conda activate rapp-tool
python -m rapp.gui
```

For a headless run, settings are provided. To run an example evaluation, simply execute

```bash
python -m rapp --config-file settings/GUI/cs/first_term_ects/cs_first_term_ects_3_dropout.ini
```

The reports are saved under `reports/`.

## BibTeX

```bibtex
@inproceedings{duong2023rapp,
  author    = {Duong, Manh Khoi AND Dunkelau, Jannik AND Cordova, Jos\'{e} Andr\'{e}s AND Conrad, Stefan},
  title     = {{RAPP}: A Responsible Academic Performance Prediction Tool for Decision-Making in Educational Institutes},
  booktitle = {BTW 2023},
  year      = {2023},
  month     = mar,
  pages     = {595--606},
  publisher = {Gesellschaft für Informatik e.V.},
  doi       = {10.18420/BTW2023-29},
}
```
