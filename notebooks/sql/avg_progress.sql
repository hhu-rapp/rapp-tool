SELECT
  SSP.Pseudonym,
  SSP.Fachsemester,
  avg(SSP.Note) as AvgNote,
  sum(SSP.Note) as SummeNoten,
  count(SSP.Note) as AnzahlNoten,
  sum(SSP.ECTS) as Ects,
  SSP.Studienfach,
  SSP.Abschluss,
  E.Bestanden,
  max(SSP.Semesterjahr) as MaxSemesterjahr
FROM
  Student_schreibt_Pruefung as SSP
INNER JOIN Einschreibung E on E.Pseudonym = SSP.Pseudonym and E.Abschluss = SSP.Abschluss and E.Studienfach = SSP.Studienfach
WHERE SSP.Abschluss = 'Bachelor'
  and SSP.Studienfach = 'Informatik'
GROUP BY SSP.Pseudonym, SSP.Fachsemester
