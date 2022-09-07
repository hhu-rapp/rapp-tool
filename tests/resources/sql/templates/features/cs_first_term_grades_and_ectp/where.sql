AND E.Studienfach = "Informatik"
AND E.Abschluss = "Bachelor"
AND SSP.Fachsemester = 1
AND SSP.Studienfach = E.Studienfach
AND SSP.Abschluss = E.Abschluss
-- Only consider since PO 2007
AND '2007-01-01' <= date(E.Immatrikulationsdatum)
