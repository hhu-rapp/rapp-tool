AND E.Studienfach = "Sozialwiss.- Medien, Pol."
AND E.Abschluss like "bachelor%"
AND SSP.Studienfach = E.Studienfach
AND SSP.Abschluss = E.Abschluss
-- Make sure we only have students which took part in at least one of these
AND NOT (EV_AP.Versuche IS NULL
          AND EV2_AP.Versuche IS NULL
          AND Sozi_AP.Versuche IS NULL
          AND Polit_AP.Versuche IS NULL
          AND Komm_AP.Versuche IS NULL
          )
-- Only consider since PO 2007
AND '2007-01-01' <= date(E.Immatrikulationsdatum)
