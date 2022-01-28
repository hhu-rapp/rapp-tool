# Pipeline Konfigurationseinstellungen

Dieses Handbuch soll dabei verhelfen eine Konfigurationsdatei ```config.ini``` zu erstellen, sodass es der Pipeline wie folgt übergeben werden kann:

```bash
python -m rapp --config-file settings/pipeline/config.ini
```

## Notwendige Argumente

Die notwendigen Argumente sind:

- `filename`: Pfad der Datenbank
- `studies_id` : Studiengang Id für die SQL Anfrage Mögliche Optionen: `cs` , `sw`
- `features_id`: Feature Id für die SQL Anfrage Mögliche Optionen: `first_term_modules`, `first_term_grades`, `first_term_ects`, `first_term_grades_and_ectp`
- `labels_id`:  Id der abhängigen Variable bzw. der zu vorhersagenden Variable: `3_dropout`, `4term_ap`, `4term_cp`, `master_admision`, `rsz`
- `categorical`: Liste von kategorischen Attribute in Form von `[attribut1, attribut2]` 
- `type`: Angabe des Aufgabentyps. Mögliche Optionen: `regression`, `classification`


## Optionale Argumente

- `label_name`: Name der abhängigen Variable bzw. der zu vorhersagenden Variable
- `imputation`: Methode um fehlende Einträge zu füllen. Mögliche Optionen: `iterative`
- `feature_selection`: Methode um irrelevante Features zu filtern. Mögliche Optionen: `variance`
- `report_path`: Pfad der Report Datei 

## Beispiel Konfiguration

```ini
# required
filename=data/rapp.db
studies_id=cs
features_id=first_term_modules
labels_id=3_dropout
categorical=[Geschlecht]
type=classification

# optional
label_name=Dropout
imputation=iterative
feature_selection=variance
report_path='reports'
```
