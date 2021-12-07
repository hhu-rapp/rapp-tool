# GUI Verbesserungen

## Oberfläche
- [ ] Log Fenster für Fehler/Ergebnisse
- [ ] Deskriptive Statistik (Plots usw.) für angefertigte SQL Anfragen
  - [ ] Diskussion: Wo in der GUI? Was soll angezeigt werden? Klassenverteilungen?
  - [ ] Mean, Std für reelle Datentypen
  - [ ] Histogramme für nominale, ordinale Datentypen
- [ ] Title Bar als Menubar verwenden (Menüleiste an der Fensterleiste setzen)
- [x] SQL Textfeld mit Dataframe Viewer tauschen
- [x] Datenbank Viewer und SQL Editor sollen fix bleiben

## Backend
- [x] Catch Exception bei fehlerhaften SQL Anfragen
- [ ] Pipeline
    - [ ] Training implementieren
    - [ ] Validate in der Pipeline implementieren für Ergebnisse (Reports: Jannik + Manh Khoi + José)
    - [ ] Catch Exception bei falschen Eingabewerten für die Pipeline
    - [ ] Tickbox bei kategorischen Variablen
    - [ ] Dropdown Menü bei Target Variable
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
  - [ ] Einbinden von Metriken an die Pipeline
  - [ ] FAML soll mit Ergebnissen/Modellen der Pipeline weiterarbeiten
- [x] GUI Code umorganisieren (eventuell neu implementieren)
  - [x] Horizontal Layout Oberfläche: Menubar, Inhalt, Statusleiste
  - [x] Inhalt (Vertikal Layout): Datenbank, Konfigurierbarer Inhalt
  - [x] Konfig. Inhalt (Horizontal Layout): Tabs
  - [x] Neue Tab = Neue Python Datei
  - [ ] Diskussion: Globale Variablen im gui.init? Übergabe von QMainWindow als self an andere QWidgets?

## Optional (geringe Priorität)
- [ ] SQL Syntax Highlighting
- [ ] Edit Menü (Copy & Paste) Implementierung
- [x] Tastenkürzel für SQL Anfrage ausführen
- [x] Tastenkürzel für Undo/Redo
- [x] Tastenkürzel für open database/open sql query