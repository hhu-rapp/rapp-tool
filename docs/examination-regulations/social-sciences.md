# Sozialwissenschaften - Medien, Politik, Gesellschaft

Übersicht über die Prüfungsordnungen (POs) des Studiengangs
"Sozialwissenschaften - Medien, Politik, Gesellschaft".
Neben der Information, welche Pflichtmodule in den ersten zwei Semestern
existieren, werden ebenfalls die Zuordnungen zwischen offiziellen Bezeichnungen
in den POs sowie den genutzen Bezeichnern in der Datenbank genutzt.

<!-- TOC -->

* [Prüfungsordnungen Pflichtmodule](#pr%C3%BCfungsordnungen-pflichtmodule)
  * [PO 2013](#po-2013)
  * [PO 2018](#po-2018)
* [Module in der Datenbank](#module-in-der-datenbank)
  * [SQL-Abfrage](#sql-abfrage)
  * [Modultabelle](#modultabelle)
* [Zuordnung PO zu Datenbank](#zuordnung-po-zu-datenbank)

<!-- /TOC -->

## Prüfungsordnungen (Pflichtmodule)

Kürzel | Bedeutung
------ | ----------
Ü      | Übung
VL     | Vorlesung
BÜ     | Basisübung
AP     | Abschlussprüfung
BN     | Beteiligungsnachweis

### PO 2013

* Erstes Semester:

  Modul                                     | Typ | AP
  ------------------------------------------|-----|----
  Einführung in die Technik wiss. Arbeitens | Ü   |
  EDV/Multimedia                            | Ü   |
  Erhebungsverfahren I                      | VL  | AP
  Soziologie I                              | VL  |
  Politikwissenschaft I                     | VL  |
  Kommunikations- und Medienwissenschaft I  | VL  |
  Soziologie I                              | BÜ  |
  Politikwissenschaft I                     | BÜ  |
  Kommunikations- und Medienwissenschaft I  | BÜ  |

* Zweites Semester:

  Modul                                     | Typ | AP
  ------------------------------------------|-----|----
  Erhebungsverfahren II                     | VL  | AP
  Soziologie II                             | VL  | AP
  Politikwissenschaft II                    | VL  | AP
  Kommunikations- und Medienwissenschaft II | VL  | AP
  Soziologie II                             | BÜ  |
  Politikwissenschaft II                    | BÜ  |
  Kommunikations- und Medienwissenschaft II | BÜ  |

### PO 2018

* Erstes Semester:

  Praxismodul Propädeutik                        | Typ | Pnr.
  -----------------------------------------------|-----|------
  Übung Techniken wissenschaftlichen Arbeitens 1 | Ü   | 5811
  Übung EDV/Multimedia                           | Ü   | 5802
  Übung Kommunikative Kompetenz                  | Ü   | 5803

  Methodenmodul Erhebungsverfahren               | Typ | Pnr.
  -----------------------------------------------|-----|------
  Vorlesung Erhebungsverfahren 1                 | VL  | 2101
  Modulabschlussprüfung Erhebungsverfahren 1     | AP  | 2110

  Basismodul Soziologie                           | Typ | Pnr.
  ------------------------------------------------|-----|------
  Vorlesung Grundlagen der Soziologie             | VL  | 1101
  Übung Einführung in die Soziologische Theorie 1 | Ü   | 1103

  Basismodul Politikwissenschaft                  | Typ | Pnr.
  ------------------------------------------------|-----|------
  Vorlesung Einführung der Politikwissenschaft    | VL  | 1201
  Übung Einführung in die Politische Theorie      | Ü   | 1203

  Basismodul Kommunikations- und Medienwissenschaft    | Typ | Pnr.
  -----------------------------------------------------|-----|------
  Vorlesung Einführung das Mediensystem in Deutschland | VL  | 1301
  Übung Das Mediensystem Deutschland                   | Ü   | 1303

* Zweites Semester:

  Methodenmodul Erhebungsverfahren               | Typ | Pnr.
  -----------------------------------------------|-----|------
  Vorlesung Erhebungsverfahren 2                 | VL  | 2102
  Modulabschlussprüfung Erhebungsverfahren 2     | AP  | 2120

  Basismodul Soziologie                           | Typ | Pnr.
  ------------------------------------------------|-----|------
  Vorlesung Die Sozialstruktur Deutschlands       | VL  | 1102
  Übung Einführung in die Soziologische Theorie 2 | Ü   | 1104
  Modulabschlussprüfung (Klausur)                 | AP  | 1110

  Basismodul Politikwissenschaft                             | Typ | Pnr.
  -----------------------------------------------------------|-----|------
  Vorlesung Einführung in das politische System Deutschlands | VL  | 1202
  Übung Einführung in die Analyse politischer Systeme        | Ü   | 1204
  Modulabschlussprüfung (Klausur)                            | AP  | 1210

  Basismodul Kommunikations- und Medienwissenschaft                                        | Typ | Pnr.
  -----------------------------------------------------------------------------------------|-----|------
  Vorlesung Einführung in die Kommunikations- und Medienwissenschaft                       | VL  | 1302
  Übung Grundbegriffe, Schwerpunkte und Modelle der Kommunikations- und Medienwissenschaft | Ü   | 1304
  Modulabschlussprüfung (Klausur)                                                          | AP  | 1310

## Module in der Datenbank

Die folgenden Module befinden sich in der Datenbank und müssen den obigen
Modulen der POs zugeordnet werden.
Sie wurden durch unten stehende SQL-Abfrage gefunden.

### SQL-Abfrage

```sql
SELECT
  P.Modul,
  P.Version,
  P.Nummer,
  SSP.Studienfach,
  case when avg(SSP.Note) is not null then "Ja" else "Nein" end as Benotet,
  count(SSP.Pseudonym) as Eintraege
FROM
  Student_schreibt_Pruefung as SSP,
  Pruefung as P
WHERE P.Nummer = SSP.Nummer
  AND P.Version = SSP.Version
  AND SSP.Fachsemester <= 2
  AND SSP.Abschluss like 'bachelor%'
  AND SSP.Studienfach in ("Sozialwiss.- Medien, Pol.", "Sozialwissenschaften")
GROUP BY P.Version, P.Nummer
HAVING Eintraege > 30 -- Ignore insignificant entries, cut-off 30 is arbitrary.
ORDER BY Studienfach, P.Version DESC, P.Nummer ASC
```

### Modultabelle

Modul                                                                                | Version | Nummer | Studienfach               | Benotet | Eintraege
------------------------------------------------------------------------------------ | ------- | ------ | ------------------------- | ------- | ---------
AP Basismodul Kommunikations- und Medienwissenschaft (Klausur)                       | 2018    | 1310   | Sozialwiss.- Medien, Pol. | Ja      | 362
AP Basismodul Politikwissenschaft (Klausur)                                          | 2018    | 1210   | Sozialwiss.- Medien, Pol. | Ja      | 245
AP Basismodul Soziologie (Klausur)                                                   | 2018    | 1110   | Sozialwiss.- Medien, Pol. | Ja      | 338
AP Erhebungsverfahren I (Klausur)                                                    | 2018    | 2110   | Sozialwiss.- Medien, Pol. | Ja      | 533
AP Erhebungsverfahren II (Klausur)                                                   | 2018    | 2120   | Sozialwiss.- Medien, Pol. | Ja      | 333
Einführung in das politische System Deutschlands                                     | 2018    | 1202   | Sozialwiss.- Medien, Pol. | Nein    | 209
Einführung in die Politikwissenschaft                                                | 2018    | 1201   | Sozialwiss.- Medien, Pol. | Nein    | 209
Einführung in die Soziologie                                                         | 2018    | 1101   | Sozialwiss.- Medien, Pol. | Nein    | 298
Erhebungsverfahren I                                                                 | 2013    | 1210   | Sozialwiss.- Medien, Pol. | Ja      | 873
Erhebungsverfahren I                                                                 | 2011    | 1210   | Sozialwiss.- Medien, Pol. | Ja      | 364
Erhebungsverfahren I                                                                 | 2005    | 1210   | Sozialwissenschaften      | Ja      | 132
Erhebungsverfahren II                                                                | 2013    | 1220   | Sozialwiss.- Medien, Pol. | Ja      | 773
Erhebungsverfahren II                                                                | 2011    | 1220   | Sozialwiss.- Medien, Pol. | Ja      | 258
Erhebungsverfahren II                                                                | 2005    | 1220   | Sozialwissenschaften      | Ja      | 106
Kommunikations- und Medienwissenschaft                                               | 2013    | 1130   | Sozialwiss.- Medien, Pol. | Ja      | 655
Kommunikations- und Medienwissenschaft                                               | 2011    | 1130   | Sozialwiss.- Medien, Pol. | Ja      | 301
Kommunikations- und Medienwissenschaft                                               | 2005    | 1130   | Sozialwissenschaften      | Ja      | 34
LV (2 CP) nach Wahl im FÜW - Orientierungsmodul                                      | 2018    | 7121   | Sozialwiss.- Medien, Pol. | Nein    | 53
Politikwissenschaft                                                                  | 2013    | 1120   | Sozialwiss.- Medien, Pol. | Ja      | 692
Politikwissenschaft                                                                  | 2011    | 1120   | Sozialwiss.- Medien, Pol. | Ja      | 314
Politikwissenschaft                                                                  | 2005    | 1120   | Sozialwissenschaften      | Ja      | 103
Sozialstruktur der Bundesrepublik Deutschland                                        | 2018    | 1102   | Sozialwiss.- Medien, Pol. | Nein    | 296
Soziologie                                                                           | 2013    | 1110   | Sozialwiss.- Medien, Pol. | Ja      | 402
Soziologie                                                                           | 2011    | 1110   | Sozialwiss.- Medien, Pol. | Ja      | 200
Soziologie                                                                           | 2005    | 1110   | Sozialwissenschaften      | Ja      | 96
VL Einführung in das Mediensystem in Deutschland                                     | 2018    | 1301   | Sozialwiss.- Medien, Pol. | Nein    | 520
VL Einführung in die Kommunikations- und Medienwissenschaft                          | 2018    | 1302   | Sozialwiss.- Medien, Pol. | Nein    | 222
Vorlesung Erhebungsverfahren I                                                       | 2018    | 2101   | Sozialwiss.- Medien, Pol. | Nein    | 506
Vorlesung Erhebungsverfahren II                                                      | 2018    | 2102   | Sozialwiss.- Medien, Pol. | Nein    | 142
Ü Das Mediensystem in Deutschland                                                    | 2018    | 1303   | Sozialwiss.- Medien, Pol. | Nein    | 520
Ü EDV/Multimedia                                                                     | 2018    | 5802   | Sozialwiss.- Medien, Pol. | Nein    | 240
Ü Einführung in die Analyse politischer Systeme                                      | 2018    | 1204   | Sozialwiss.- Medien, Pol. | Nein    | 337
Ü Einführung in die Politische Theorie                                               | 2018    | 1203   | Sozialwiss.- Medien, Pol. | Nein    | 529
Ü Einführung in die soziologische Theorie I                                          | 2018    | 1103   | Sozialwiss.- Medien, Pol. | Nein    | 380
Ü Einführung in die soziologische Theorie II                                         | 2018    | 1104   | Sozialwiss.- Medien, Pol. | Nein    | 485
Ü Grundbegriffe, Schwerpunkte und Modelle der Kommunikations- und Medienwissenschaft | 2018    | 1304   | Sozialwiss.- Medien, Pol. | Nein    | 317
Ü Kommunikative Kompetenz                                                            | 2018    | 5803   | Sozialwiss.- Medien, Pol. | Nein    | 133
Ü Techniken wissenschaftlichen Arbeitens I (1\. Semester)                            | 2018    | 5811   | Sozialwiss.- Medien, Pol. | Nein    | 152
Ü Techniken wissenschaftlichen Arbeitens I + II                                      | 2018    | 5801   | Sozialwiss.- Medien, Pol. | Nein    | 214

## Zuordnung PO zu Datenbank

Obwohl sowohl die PO 2013 als auch die PO 2018 zwischen Vorlesung, Übung und
Abschlussprüfung für die Basismodule und 'Erhebungsverfahren' unterscheiden,
scheint es nur für 2018 differenzierte Einträge in der Datenbank zu geben.

Für das Praxismodul Propädeutik scheint es für 2013 keine Einträge zu geben
(bzw. exakt drei).

* Erstes Semester:
  * Praxismodul Propädeutik
    * "Ü Techniken wissenschaftlichen Arbeitens I (1\. Semester)", Version: 2018, Pnr.: 5811, benotet: Nein
    * "Ü EDV/Multimedia", Version: 2018, Pnr.: 5802, benotet: Nein
    * "Ü Kommunikative Kompetenz", Version: 2018, Pnr.: 5803, benotet: Nein
  * Methodenmodul Erhebungsverfahren
    * "Vorlesung Erhebungsverfahren I", Version: 2018, Pnr.: 2101, benotet: Nein
    * "AP Erhebungsverfahren I (Klausur)", Version: 2018, Pnr.: 2110, benotet: Ja
      * "Erhebungsverfahren I", Version: 2013, Pnr.: 1210, benotet: Ja
      * "Erhebungsverfahren I", Version: 2011, Pnr.: 1210, benotet: Ja
  * Basismodul Soziologie
    * "Einführung in die Soziologie", Version: 2018, Pnr.: 1101, benotet: Nein
    * "Ü Einführung in die soziologische Theorie I", Version: 2018, Pnr.: 1103, benotet: Nein
  * Basismodul Politikwissenschaft
    * "Einführung in die Politikwissenschaft", Version: 2018, Pnr.: 1201, benotet: Nein
    * "Ü Einführung in die Politische Theorie", Version: 2018, Pnr.: 1203, benotet: Nein
  * Basismodul Kommunikations
    * "VL Einführung in das Mediensystem in Deutschland", Version: 2018, Pnr.: 1301, benotet: Nein
    * "Ü Das Mediensystem in Deutschland", Version: 2018, Pnr.: 1303, benotet: Nein
* Zweites Semester:
  * Methodenmodul Erhebungsverfahren
    * "Vorlesung Erhebungsverfahren II", Version: 2018, Pnr.: 2102, benotet: Nein
    * "AP Erhebungsverfahren II (Klausur)", Version: 2018, Pnr.: 2120, benotet: Ja
      * "Erhebungsverfahren II", Version: 2013, Pnr.: 1220, benotet: Ja
      * "Erhebungsverfahren II", Version: 2011, Pnr.: 1220, benotet: Ja
  * Basismodul Soziologie
    * "Sozialstruktur der Bundesrepublik Deutschland", Version: 2018, Pnr.: 1102, benotet: Nein
    * "Ü Einführung in die soziologische Theorie II", Version: 2018, Pnr.: 1104, benotet: Nein
    * "AP Basismodul Soziologie (Klausur)", Version: 2018, Pnr.: 1110, benotet: Ja
      * "Soziologie", Version: 2013, Pnr.: 1110, benotet: Ja
      * "Soziologie", Version: 2011, Pnr.: 1110, benotet: Ja
  * Basismodul Politikwissenschaft
    * "Einführung in das politische System Deutschlands", Version: 2018, Pnr.: 1202, benotet: Nein
    * "Ü Einführung in die Analyse politischer Systeme", Version: 2018, Pnr.: 1204, benotet: Nein
    * "AP Basismodul Politikwissenschaft (Klausur)", Version: 2018, Pnr.: 1210, benotet: Ja
      * "Politikwissenschaft", Version: 2013, Pnr.: 1120, benotet: Ja
      * "Politikwissenschaft", Version: 2011, Pnr.: 1120, benotet: Ja
  * Basismodul Kommunikations
    * "VL Einführung in die Kommunikations- und Medienwissenschaft", Version: 2018, Pnr.: 1302, benotet: Nein
    * "Ü Grundbegriffe, Schwerpunkte und Modelle der Kommunikations- und Medienwissenschaft", Version: 2018, Pnr.: 1304, benotet: Nein
    * "AP Basismodul Kommunikations- und Medienwissenschaft (Klausur)", Version: 2018, Pnr.: 1310, benotet: Ja
      * "Kommunikations- und Medienwissenschaft", Version: 2013, Pnr.: 1130, benotet: Ja
      * "Kommunikations- und Medienwissenschaft", Version: 2011, Pnr.: 1130, benotet: Ja
* Nicht zugeordnet
  * "Ü Techniken wissenschaftlichen Arbeitens I + II", Version: 2018, Pnr.: 5801, benotet: Nein
  * Studiengang "Soziologie"
    * "Soziologie", Version: 2005, Pnr.: 1110, benotet: Ja
    * "Politikwissenschaft", Version: 2005, Pnr.: 1120, benotet: Ja
    * "Kommunikations- und Medienwissenschaft", Version: 2005, Pnr.: 1130, benotet: Ja
    * "Erhebungsverfahren I", Version: 2005, Pnr.: 1210, benotet: Ja
    * "Erhebungsverfahren II", Version: 2005, Pnr.: 1220, benotet: Ja
