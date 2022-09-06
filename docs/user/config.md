# Pipeline Configuration settings

This manual should help to create a configuration file `config.ini` so that it can be loaded in the GUI:

## Required arguments

The required arguments are:

- `filename`: directory of database
- `studies_id` : Study program Id for the SQL query. Possible options: `cs` , `sw`
- `features_id`: Feature Id for the SQL query. Possible options: `first_term_modules`, `first_term_grades`, `first_term_ects`, `first_term_grades_and_ectp`
- `labels_id`:  Id of the dependent variable or the variable to be predicted: `3_dropout`, `4term_ap`, `4term_cp`, `master_admission`, `rsz`


## Optionale Argumente

- `label_name`: Name of the dependent variable or the variable to be predicted
- `sensitive_attributes`:  List of categorical attributes in the form of: `[Geschlecht, Deutsch]`
- `type`: Specification of the task type. Possible options: `classification`,`regression`
- `estimators`: List of Estimators to be trained. For`type=classification`:`[RF,SVM,DT,NB,LR]`. For `type=regression` :`[EL,LR,BR]`


## Beispiel Konfiguration

```ini
[required]
filename=data/rapp.db
studies_id=cs
features_id=first_term_modules
labels_id=3_dropout

[optional]
label_name=Dropout
sensitive_attributes=[Geschlecht, Deutsch]
type=classification
estimators=[RF,SVM,DT,NB,LR]

```
