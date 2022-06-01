LEFT JOIN
  (SELECT -- FirstTermData
    SSP.Pseudonym,
    SUM(SSP.ECTS) as Ectp,
    AVG(CASE WHEN SSP.Note <> 0 AND SSP.Status = 'bestanden'
        THEN SSP.NOTE ELSE null END) as DurchschnittsNoteBestanden,
    AVG(SSP.NOTE) as DurchschnittsNoteTotal,
    COUNT(SSP.Pseudonym) as KlausurenGeschrieben,
    COUNT(CASE WHEN SSP.Status = 'bestanden'
               THEN SSP.Pseudonym ELSE null END ) as KlausurenBestanden,
    COUNT(CASE WHEN SSP.Status <> 'bestanden'
               THEN SSP.Pseudonym ELSE null END ) as KlausurenNichtBestanden
  FROM
    Student_schreibt_Pruefung as SSP
  WHERE SSP.Studienfach = "Sozialwiss.- Medien, Pol."
    AND SSP.Abschluss like "bachelor%"
    AND SSP.Fachsemester = 1
  GROUP BY SSP.Pseudonym
  HAVING KlausurenGeschrieben > 0 -- Ignore entries with no recorded first semester.
  ) as FirstTermData
  ON FirstTermData.Pseudonym = SSP.Pseudonym
