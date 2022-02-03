SELECT
-- Dropout.Dropout,
SUM(CASE WHEN SSP.Fachsemester <= 4 AND SSP.Status = 'bestanden'
                    THEN 1 ELSE 0 END) as
  FourthTermAP,
SUM(CASE WHEN SSP.Fachsemester <= 4 THEN SSP.ECTS ELSE 0 END)
  as FourthTermCP,
FinalGrade.Grade,
FinalGrade.LastTerm
FROM
  Student as S,
  Student_schreibt_Pruefung as SSP,
  Pruefung as P,
  Einschreibung as E
-- INNER JOIN
--   (SELECT
--     S.Pseudonym,
--     E.Studienfach,
--     E.Abschluss,
--     -- E.Bestanden,
--     -- LetztePruefung.SemesterCode,
--     CASE WHEN LetztePruefung.SemesterCode < 20192 THEN NOT E.Bestanden ELSE null END as Dropout
--     -- 20192 is the code for wintersemester 2019 (summersemester would be 20191).
--     -- This is three terms ago, given the age of the dataset.
--     -- Thus, everybody not writing an exam in the last three terms is assumed
--     -- to have ended their studyship, and those whom did not graduate are deemed
--     -- as dropouts.
--   FROM
--     Student as S,
--     Einschreibung as E
--   JOIN
--     (SELECT
--       SSP.Pseudonym,
--       max(SSP.Semesterjahr*10 + (2-SSP.Sommersemester)) as SemesterCode
--     FROM
--       Student_schreibt_Pruefung as SSP
--     GROUP BY SSP.Pseudonym
--     ) as LetztePruefung
--     ON S.Pseudonym = LetztePruefung.Pseudonym
--   WHERE S.Pseudonym = E.Pseudonym
--   ) as Dropout ON Dropout.Pseudonym = S.Pseudonym
INNER JOIN
  (SELECT
    S.Pseudonym,
    avg(SSP.Note) as Grade,
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
    and E.Studienfach = SSP.Studienfach
    and E.Abschluss = SSP.Abschluss
  GROUP BY S.Pseudonym) as FinalGrade
  on FinalGrade.Pseudonym = S.Pseudonym



WHERE
    S.Pseudonym = SSP.Pseudonym
AND S.Pseudonym = E.Pseudonym
AND SSP.Version = P.Version
AND SSP.Nummer = P.Nummer
AND E.Studienfach = "Informatik"
AND E.Abschluss = "Bachelor"
-- AND SSP.Fachsemester = 1
AND SSP.Studienfach = E.Studienfach
AND SSP.Abschluss = E.Abschluss
-- AND Dropout.Studienfach = E.Studienfach
-- AND Dropout.Abschluss = E.Abschluss
-- AND Dropout.Dropout IN (0, 1)  -- NULL-Entries are sorted out
AND FinalGrade.Pseudonym = E.Pseudonym
AND FinalGrade.Studienfach = E.Studienfach
AND FinalGrade.Abschluss = E.Abschluss
AND '2007-01-01' <= date(E.Immatrikulationsdatum)


GROUP BY S.Pseudonym
