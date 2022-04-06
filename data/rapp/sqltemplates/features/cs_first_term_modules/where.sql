AND E.Studienfach = "Informatik"
AND E.Abschluss = "Bachelor"
AND SSP.Studienfach = E.Studienfach
AND SSP.Abschluss = E.Abschluss
-- Make sure we only have students which took part in at least one of these
AND NOT (LA.Versuche IS NULL AND Prog.Versuche IS NULL AND Ana.Versuche IS NULL)
-- Only consider since PO 2007
AND '2007-01-01' <= date(E.Immatrikulationsdatum)
