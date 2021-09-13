-- Features: Performances in first semester
--
-- Note:
-- * The average grade is not the weighted average grade used for the official
--   final grade on the table of records, as we lack information for this
--   (which exam was Wahlpflicht, which was Schwerpunkt, ...)
SELECT
  S.Geburtsjahr,
  S.Geschlecht,
  S.Deutsch,
  strftime("%Y", E.Immatrikulationsdatum) - S.Geburtsjahr as AlterEinschreibung,
  FirstTermData.KlausurenGeschrieben,
  FirstTermData.KlausurenBestanden,
  FirstTermData.Ects,
  CASE WHEN FirstTermData.DurchschnittsNote IS NULL then 5 else FirstTermData.DurchschnittsNote end as DurchschnittsNote,
  CASE WHEN FirstTermData.DurchschnittsNote IS NULL then 0 else
    (SUM(CASE WHEN SSP.Note <> 0 AND SSP.Status = 'bestanden'
        THEN (SSP.NOTE-FirstTermData.DurchschnittsNote)*(SSP.NOTE-FirstTermData.DurchschnittsNote)
        ELSE NULL END)
      / FirstTermData.KlausurenBestanden)
  END as StdevNoteQuadriert,
  Dropout.Dropout
FROM
  Student as S,
  Student_schreibt_Pruefung as SSP,
  Pruefung as P,
  Einschreibung as E,
  (SELECT -- FirstTermData
    SSP.Pseudonym,
    SUM(SSP.ECTS) as Ects,
    AVG(CASE WHEN SSP.Note <> 0 AND SSP.Status = 'bestanden' THEN SSP.NOTE ELSE null END) as DurchschnittsNote,
    COUNT(SSP.Pseudonym) as KlausurenGeschrieben,
    COUNT(CASE WHEN SSP.Status = 'bestanden' THEN SSP.Pseudonym ELSE null END ) as KlausurenBestanden
  FROM
    Student_schreibt_Pruefung as SSP
  WHERE SSP.Studienfach = "Informatik"
    AND SSP.Abschluss = "Bachelor"
    AND SSP.Fachsemester = 1
  GROUP BY SSP.Pseudonym
  HAVING KlausurenGeschrieben > 0 -- Ignore entries with no recorded first semester.
  ) as FirstTermData
INNER JOIN
  (SELECT -- dropout_no_exam_last_three_terms.sql
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
  ) as Dropout ON Dropout.Pseudonym = S.Pseudonym
WHERE S.Pseudonym = SSP.Pseudonym
  AND FirstTermData.Pseudonym = S.Pseudonym
  AND S.Pseudonym = E.Pseudonym
  AND SSP.Version = P.Version
  AND SSP.Nummer = P.Nummer
  AND E.Studienfach = "Informatik"
  AND E.Abschluss = "Bachelor"
  AND SSP.Studienfach = E.Studienfach
  AND SSP.Abschluss = E.Abschluss
  AND Dropout.Studienfach = E.Studienfach
  AND Dropout.Abschluss = E.Abschluss
  AND SSP.Fachsemester = 1
  AND Dropout.Dropout IN (0, 1) -- NULL-Entries are sorted out
GROUP BY S.Pseudonym
