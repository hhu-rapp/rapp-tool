INNER JOIN
  (SELECT
    S.Pseudonym,
    max(SSP.Fachsemester) as LastTerm,
    E.Studienfach,
    E.Abschluss
  FROM
    Student as S,
    Student_schreibt_Pruefung as SSP,
    Einschreibung as E
  WHERE S.Pseudonym = E.Pseudonym
    and S.Pseudonym = SSP.Pseudonym
    and E.bestanden = 1
    AND SSP.Studienfach = E.Studienfach
    AND SSP.Abschluss = E.Abschluss
  GROUP BY S.Pseudonym, E.Studienfach, E.Abschluss) as TermsNeeded
