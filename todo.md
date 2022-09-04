# AP1 Todo (Allgemeine Planung)

## GUI

- [ ] Wahl zwischen Entwicklermodus und Anwender
  - Nützlich für potentielle Anwender, die sich nicht mit SQL auskennen
  - [ ] Anwendermodus
    - [ ] Vorgefertigte Konfigurationen für Anwender
      - [ ] Nach Studienfächer
      - [ ] Nach Semester
- [x] Log Fenster für Fehler/Ergebnisse
  - [x] Logging TextBrowser eigenes Objekt und append wird überschrieben
  - [x] Prints ins Log Fenster schreiben
    - [x] ~~*SQL Exceptions*~~
    - [x] ~~*Datenbank laden [Jose]*~~
    - [x] ~~*SQL Anfragen laden [Jose]*~~
    - [x] ~~*SQL Anfragen speichern [Jose]*~~
    - [x] Fehlerhafte Angaben bei der Pipeline [Jose, hoehere Prio]
  - [x] ~~*Log Fenster hinzugefügt*~~
- [x] Deskriptive Statistik (Plots usw.) für angefertigte SQL Anfragen
  - [x] Diskussion: Wo in der GUI? Was soll angezeigt werden? Klassenverteilungen?
  - [x] Mean, Std für reelle Datentypen
  - [x] Histogramme für nominale, ordinale Datentypen
- [ ] Title Bar als Menubar verwenden (Menüleiste an der Fensterleiste setzen) [Jose, geringe prio]
- Backend
  - [x] Pipeline
        - [x] Training implementieren/fixen [Jose, hoehere Prio]
        - [x] ML Pipeline ueberarbeiten, sodass Pandas DF uebergeben werden koennen [Jose]
        - [x] Validate in der Pipeline implementieren für Ergebnisse (Reports: Jannik + Manh Khoi + José)
        - [x] Catch Exception bei falschen Eingabewerten für die Pipeline
        - [x] Tickbox bei kategorischen Variablen bzw. komplett automatisieren [Jose]
        - [x] Kategorischen Variablen lineEdit verbessern [Jose]
          - [x] Dropdown Menü bei Target Variable
        - [ ] Einbinden von Reports an die GUI
  - [ ] Explainable AI Tab einsetzen (Jannik + Manh Khoi Austausch)
    - [ ] Diskussion der Darstellung
    - [ ] Einbinden von xAI an die GUI
    - [ ] xAI soll mit Ergebnisse der Pipeline weiterarbeiten
    - [ ] Jeder Klassifikator erhält eine eigene xAI
      - [ ] Black-Box Modelle werden durch PDE/ICE, SHAP, Lime etc. erklärt (model-agnostic)
      - [ ] White-Box Modelle werden durch ihr eigenes Modell erklärt
      - [ ] Diskussion: Darstellung der Erklärungen in der GUI
  - [ ] Fairness-Aware Machine Learning
    - [x] Einbinden von Metriken an die Pipeline
    - [x] FAML soll mit Ergebnissen/Modellen der Pipeline weiterarbeiten
  - [x] ~~*GUI Code umorganisieren (eventuell neu implementieren)*~~
    - [x] ~~*Horizontal Layout Oberfläche: Menubar, Inhalt, Statusleiste*~~
    - [x] ~~*Inhalt (Vertikal Layout): Datenbank, Konfigurierbarer Inhalt*~~
    - [x] ~~*Konfig. Inhalt (Horizontal Layout): Tabs*~~
    - [x] ~~*Neue Tab = Neue Python Datei*~~
    - [ ] Diskussion: Globale Variablen im gui.init? Übergabe von QMainWindow als self an andere QWidgets?
- [ ] SQL Syntax Highlighting
- [x] Edit Menü (Copy & Paste) Implementierung

## Predictions

- [ ] Implementierung der Predictions wie besprochen im Konsortium
  - [ ] Erstelle SQL-Abfragen für verschiedene Features
    - [ ] ECTS Erstes Semester
    - [ ] Noten im ersten Semester
      - [ ] mean
      - [ ] stdev
    - [ ] Anzahl NBs
