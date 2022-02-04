# Pipeline Konfigurationseinstellungen

Dieses Handbuch soll dabei verhelfen eine Konfigurationsdatei `config.ini` zu erstellen, sodass sie in der GUI geladen werden kann:

## Notwendige Argumente

Die notwendigen Argumente sind:

- `filename`: Pfad der Datenbank
- `studies_id` : Studiengang Id für die SQL Anfrage Mögliche Optionen: `cs` , `sw`
- `features_id`: Feature Id für die SQL Anfrage Mögliche Optionen: `first_term_modules`, `first_term_grades`, `first_term_ects`, `first_term_grades_and_ectp`
- `labels_id`:  Id der abhängigen Variable bzw. der zu vorhersagenden Variable: `3_dropout`, `4term_ap`, `4term_cp`, `master_admission`, `rsz`


## Optionale Argumente

- `label_name`: Name der abhängigen Variable bzw. der zu vorhersagenden Variable
- `sensitive_attributes`:  Liste von kategorischen Attribute in Form von: `[Geschlecht, Deutsch]`
- `type`: Angabe des Aufgabentyps. Mögliche Optionen: `classification`,`regression`
- `estimators`:  Liste von Estimators die trainiert werden sollen. Für  `type=classification`:`[RF,SVM,DT,NB,LR]`. Für `type=regression` :`[EL,LR,BR]`


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
