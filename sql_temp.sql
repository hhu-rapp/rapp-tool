-- Dropout definition: No exams written in the last 3 terms.
--
-- Datapoints: 8990
-- Dropout samples: 3239 (36 %)
--
-- Computing students: 3199
-- Computing dropout: 1238 (39 %)
SELECT
  S.Pseudonym,
  E.Studienfach,
  E.Abschluss,
  -- E.Bestanden,
  -- LetztePruefung.SemesterCode,
  CASE WHEN LetztePruefung.SemesterCode < 20192 THEN NOT E.Bestanden ELSE null END as Dropout
  -- 20192 is the code for wintersemester 2019 (summersemester would be 20191).
  -- This is three terms ago, given the age of the dataset.
  -- Thus, everybody not writing an exam in the last three terms is assumed
  -- to have ended their studyship, and those whom did not graduate are deemed
  -- as dropouts.
FROM
  Student as S,
  Einschreibung as E
JOIN
  (SELECT
    SSP.Pseudonym,
    max(SSP.Semesterjahr*10 + (2-SSP.Sommersemester)) as SemesterCode
  FROM
    Student_schreibt_Pruefung as SSP
  GROUP BY SSP.Pseudonym
  ) as LetztePruefung
  ON S.Pseudonym = LetztePruefung.Pseudonym
WHERE S.Pseudonym = E.Pseudonym
ORDER BY S.Pseudonym
