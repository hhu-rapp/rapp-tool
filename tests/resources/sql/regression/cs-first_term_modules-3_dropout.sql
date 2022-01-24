-- Features:
--  Binary markers whether Linear Algebra, Programming (Info 1), and
--  Analysis were passed and how many attempts were used.
--  Last achieved grade in Programming. Linear Algebra and Analysis do not
--  have any recorded grades for CS students besides 0.0 (passed?) and 5.0
--  (failed).
-- Target variables:
--  Dropout defined as "no exam written in last 3 semesters"
-- Note:
--  In 2018 PO computer science switched what the first term modules are for
--  students. However, the official suggestion is to still do Analysis in
--  first term and algorithms in third, as per old POs. Allegedly, most
--  students follow this advice.
SELECT
  -- protected attributes
  -- S.Geburtsjahr,
  S.Geschlecht,
  S.Deutsch,
  strftime("%Y", E.Immatrikulationsdatum) - S.Geburtsjahr as AlterEinschreibung,
  -- Features
  case when LA.Bestanden IS NOT NULL then LA.Bestanden else 0 end as LABestanden,
  case when LA.Versuche IS NOT NULL then LA.Versuche else 0 end as LAVersuche,
  case when Prog.Bestanden IS NOT NULL then Prog.Bestanden else 0 end as ProgBestanden,
  case when Prog.Versuche IS NOT NULL then Prog.Versuche else 0 end as ProgVersuche,
  case when ProgNote.Note IS NOT NULL then ProgNote.Note else 5. end as ProgNote,
  case when Ana.Bestanden IS NOT NULL then Ana.Bestanden else 0 end as AnaBestanden,
  case when Ana.Versuche IS NOT NULL then Ana.Versuche else 0 end as AnaVersuche,
  -- Label
  Dropout.Dropout
FROM
  Student as S,
  Student_schreibt_Pruefung as SSP,
  Pruefung as P,
  Einschreibung as E
LEFT JOIN
  ( SELECT
      -- SSP.Note as Note,
      max(CASE WHEN SSP.Status = 'bestanden' then 1 else 0 end) as Bestanden,
      max(SSP.Versuch) as Versuche,
      SSP.Pseudonym
    FROM
      Student_schreibt_Pruefung as SSP,
      Pruefung as P
    WHERE P.Nummer = SSP.Nummer
      AND P.Version = SSP.Version
      AND P.Modul IN ('Lineare Algebra', 'Lineare Algebra I')
      AND SSP.Fachsemester <= 1
    GROUP BY SSP.Pseudonym
    ) as LA
  ON LA.Pseudonym = SSP.Pseudonym
LEFT JOIN
  ( SELECT
      max(CASE WHEN SSP.Status = 'bestanden' then 1 else 0 end) as Bestanden,
      max(SSP.Versuch) as Versuche,
      SSP.Pseudonym
    FROM
      Student_schreibt_Pruefung as SSP,
      Pruefung as P
    WHERE P.Nummer = SSP.Nummer
      AND P.Version = SSP.Version
      AND P.Modul IN ('Programmierung ', 'Grundlagen der Softwareentwicklung und Programmierung')
      AND SSP.Fachsemester <= 1
    GROUP BY SSP.Pseudonym
    ) as Prog
  ON Prog.Pseudonym = SSP.Pseudonym
LEFT JOIN
  ( SELECT
      SSP.Versuch,
	    SSP.Note,
      SSP.Pseudonym
    FROM
      Student_schreibt_Pruefung as SSP,
      Pruefung as P
    WHERE P.Nummer = SSP.Nummer
      AND P.Version = SSP.Version
      AND P.Modul IN ('Programmierung ', 'Grundlagen der Softwareentwicklung und Programmierung')
      AND SSP.Fachsemester <= 1
    ORDER BY SSP.Pseudonym
    ) as ProgNote
  ON Prog.Pseudonym = ProgNote.Pseudonym AND Prog.Versuche = ProgNote.Versuch
LEFT JOIN
  ( SELECT
      max(CASE WHEN SSP.Status = 'bestanden' then 1 else 0 end) as Bestanden,
      max(SSP.Versuch) as Versuche,
      SSP.Pseudonym
    FROM
      Student_schreibt_Pruefung as SSP,
      Pruefung as P
    WHERE P.Nummer = SSP.Nummer
      AND P.Version = SSP.Version
      AND P.Modul = 'Analysis I'
      AND SSP.Fachsemester <= 1
    GROUP BY SSP.Pseudonym
    ) as Ana
  ON Ana.Pseudonym = SSP.Pseudonym
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
  AND S.Pseudonym = E.Pseudonym
  AND SSP.Version = P.Version
  AND SSP.Nummer = P.Nummer
  AND E.Studienfach = "Informatik"
  AND E.Abschluss = "Bachelor"
  AND SSP.Studienfach = E.Studienfach
  AND SSP.Abschluss = E.Abschluss
  AND Dropout.Studienfach = E.Studienfach
  AND Dropout.Abschluss = E.Abschluss
  -- Make sure we only have students which took part in at least one of these
  AND NOT (LA.Versuche IS NULL AND Prog.Versuche IS NULL AND Ana.Versuche IS NULL)
  -- Only consider since PO 2007
  AND '2007-01-01' <= date(E.Immatrikulationsdatum)
  AND Dropout.Dropout IN (0, 1) -- NULL-Entries are sorted out
GROUP BY S.Pseudonym
