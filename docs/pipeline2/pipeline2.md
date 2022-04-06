# Pipeline 2.0
## Pipeline Object
- struct/dictionary
- contains all the data needed, e.g., training data, results, etc.
- other classes/files access pipeline
- all variables must be declared in _init__ (PEP 8)
- pipeline object gets parser.Namespace


## Modules
- static methods
	- access pipeline object
- only use OOP if needed (!)


## DocString
- NumPy oriented
	- describe parameters first by type and then function
	- same for returned variables

## Structure
tbd

## Used files
### rapp/
rapp/npipeline.py
rapp/__main__.py
rapp/parser.py
rapp/util.py

### rapp/fair
rapp/fair/notions.py

### rapp/report
rapp/report/reports.py
rapp/report/latex/__init __.py
rapp/report/latex/tables.py
