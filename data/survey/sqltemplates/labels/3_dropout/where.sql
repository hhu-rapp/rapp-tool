AND Dropout.Studienfach = E.Studienfach
AND Dropout.Abschluss = E.Abschluss
AND Dropout.Dropout IN (0, 1)  -- NULL-Entries are sorted out
