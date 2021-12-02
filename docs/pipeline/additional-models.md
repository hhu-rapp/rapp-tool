# Additional Models

Die als "additional models" bezeichneten Modelle in der Pipeline werden
zusätzlich trainiert, sobald Bedarf besteht.

Bedarf ist hierbei via
`rapp.pipeline.additionalmodels.tex_additional_models` definiert.

<!-- TOC -->

* [Trainieren zusätzlicher Modelle](#trainieren-zus%C3%A4tzlicher-modelle)
  * [Dispatch-Mechanismus](#dispatch-mechanismus)
* [Spezifikation: Trainingsfunktion](#spezifikation-trainingsfunktion)

<!-- /TOC -->

## Trainieren zusätzlicher Modelle

Ob für einen Estimator zusätzliche Modelle trainiert werden,
und welche dies sind,
wird von der Funktion
`rapp.pipeline.training.get_additional_models` bestimmt.
Der erste Parameter ist hierbei ein trainiertes Vorhersagemodell,
zu welchem zusätzliche Modelle trainiert werden sollen.

### Dispatch-Mechanismus

Der Dispatch wird durch `rapp.pipeline.training.get_additional_models`
definiert.
Mechanisch geschieht dies via `functools.singledispatch`-Dekoration
und Differenzierung via Typ des ersten Parameters.

Um beispielsweise für die Klasse `sklearn.tree.DecisionTreeClassifier`
zusätzliche Modelle zu trainieren,
genügt die Implementation folgender Funktion:

```python
from functools import singledispatch
from sklearn.tree import DecisionTreeClassifier

@get_additional_models.register
def _(estimator: DecisionTreeClassifier, X_train, y_train, X_val, y_val):
  pass
```

Die Angabe `estimator: DecisionTreeClassifier` spezifiziert,
dass dieser Dispatch für `DecisionTreeClassifier` geschieht.
Der Default-Dispatch gibt eine leere Liste zurück.

Statt `pass` muss natürlich der Code aufgerufen werden, der neue Modelle
trainiert.

## Spezifikation: Trainingsfunktion

Funktionen, die durch den Dispatch aufgerufen werden um zusätzliche Modelle
zu trainieren, müssen der folgenden Spezifikation gerecht werden:

Als Eingabe erhalten sie Parameter in der folgenden Reihenfolge

* `estimator`: Der fertig trainierte Estimator, zu dem neue Modelle trainiert
  werden sollen.
* `X_train`, `y_train`: Trainingsdaten
* `X_val`, `y_val`: Validierungs- oder Testdaten

Die Ausgabe ist eine Liste von Dictionaries, welche Informationen über
die Zusätzlichen Modelle beinhalten.
Folgende Keys sind dabei zu beachten:

* `model` (erforderlich):
  Hinterlegt das trainierte, zusätzliche Modell
* `safe_model` (bool, optional):
  Gibt an, ob dieses Modell in eventuellen Reports gespeichert werden sollte
  oder nicht.
  Wenn der Key nicht gesetzt wird, wird der Wert `True` angenommen.
* `save_path` (extern gesetzt):
  Gibt den Speicherort des zusätzlichen Modells an, wenn `safe_model` nicht
  `False` ist. Speichern der Modelle erfolgt vereinheitlicht in
  `rapp.pipeline.MLPipeline.train_additional_models` und dort wird `save_path`
  automatisch gesetzt.
* `id` (extern gesetzt):
  Wird extern an die zusätzlichen Modelle verteilt und sollte
  durch den Dispatch selbst nicht vergeben werden.
