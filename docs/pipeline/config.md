# Pipeline Konfigurationseinstellungen

Dieses Handbuch soll dabei verhelfen eine Konfigurationsdatei ```config.ini``` zu erstellen, sodass es der Pipeline wie folgt übergeben werden kann:

```bash
python -m rapp --config-file settings/pipeline/config.ini
```

## Notwendige Argumente

Die notwendigen Argumente sind:

- `filename`: Pfad der Datenbank
- `sql_filename`: Pfad der SQL Anfrage
- `label_name`: Name der abhängigen Variable bzw. der zu vorhersagenden Variable
- `categorical`: Liste von kategorischen Attribute in Form von `[attribut1, attribut2]` 
- `type`: Angabe des Aufgabentyps. Mögliche Optionen: `regression`, `classification`
- `report_path`: Pfad der Report Datei

## Optionale Argumente

- `imputation`: Methode um fehlende Einträge zu füllen. Mögliche Optionen: `iterative`
- `feature_selection`: Methode um irrelevante Features zu filtern. Mögliche Optionen: `variance`

## Beispiel Konfiguration

```bash
# required
filename=data/rapp.db
sql_filename=sql/CSFirstSemester.sql
label_name=AvgGrade
categorical=[Deutsch, Geschlecht]
type=regression
report_path='reports'

# optional
imputation=iterative
feature_selection=variance
```
