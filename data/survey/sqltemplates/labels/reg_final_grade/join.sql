INNER JOIN
  (SELECT
    S.Pseudonym,
    avg(SSP.Note) as Grade,
    E.Studienfach,
    E.Abschluss
  FROM
    Student as S,
    Student_schreibt_Pruefung as SSP,
    Einschreibung as E
  WHERE S.Pseudonym = E.Pseudonym
    and S.Pseudonym = SSP.Pseudonym
    and E.bestanden = 1
    and E.Studienfach = SSP.Studienfach
    and E.Abschluss = SSP.Abschluss
  GROUP BY S.Pseudonym) as FinalGrade
