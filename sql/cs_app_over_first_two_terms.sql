-- Features: Performances in first and second semester
-- Possible target variables:
--  * Average grade over all exams until graduation
--  * Master's admission (average grade <= 2.5)
--  * Bachelor's thesis grade
--
-- Note:
-- * This set only considers students which have finished their degree.
-- * The average grade is not the weighted average grade used for the official
--   final grade on the table of records, as we lack information for this
--   (which exam was Wahlpflicht, which was Schwerpunkt, ...)
SELECT
  S.Geburtsjahr,
  S.Geschlecht,
  CASE WHEN S.Deutsch = 1 THEN 'ja' ELSE 'nein' END as Deutsch,
  COUNT(CASE WHEN SSP.Fachsemester = 1 THEN SSP.Pseudonym ELSE null END ) as WrittenFirstTerm,
  COUNT(CASE WHEN SSP.Fachsemester = 1 AND SSP.Status <> 'bestanden' THEN SSP.Pseudonym ELSE null END ) as FailedFirstTerm,
  SUM(CASE WHEN SSP.Fachsemester = 1 THEN SSP.ECTS ELSE 0 END) as EctsFirstTerm,
  COUNT(CASE WHEN SSP.Fachsemester = 2 THEN SSP.Pseudonym ELSE null END ) as WrittenSecondTerm,
  COUNT(CASE WHEN SSP.Fachsemester = 2 AND SSP.Status <> 'bestanden' THEN SSP.Pseudonym ELSE null END ) as FailedSecondTerm,
  SUM(CASE WHEN SSP.Fachsemester = 2 THEN SSP.ECTS ELSE 0 END) as EctsSecondTerm,
  SUM(CASE WHEN SSP.Note > 0 THEN SSP.NOTE ELSE 0 END)/COUNT(CASE WHEN SSP.Note > 0 THEN SSP.NOTE ELSE null END) as AvgGradeAllExams,
  CASE WHEN SUM(CASE WHEN SSP.Note > 0 THEN SSP.NOTE ELSE 0 END)/COUNT(CASE WHEN SSP.Note > 0 THEN SSP.NOTE ELSE null END) <= 2.5
    THEN 'ja' ELSE 'nein' END as MasterAdmission,
  MAX(SSP.Fachsemester) as NumTerms,
  BA.Note as BachelorGrade
FROM
  Student as S,
  Student_schreibt_Pruefung as SSP,
  Pruefung as P,
  Einschreibung as E,
  ( SELECT
      SSP.Note as Note,
      SSP.Pseudonym as Pseudonym
    FROM
      Student_schreibt_Pruefung as SSP,
      Pruefung as P
    WHERE P.Nummer = SSP.Nummer
      AND P.Version = SSP.Version
      AND P.Modul LIKE 'bachelorarbeit'
    ) as BA
WHERE S.Pseudonym = SSP.Pseudonym
  AND S.Pseudonym = BA.Pseudonym
  AND S.Pseudonym = E.Pseudonym
  AND SSP.Version = P.Version
  AND SSP.Nummer = P.Nummer
  AND E.Studienfach = "Informatik"
  AND E.Abschluss = "Bachelor"
  AND E.Bestanden = 1
  AND SSP.Studienfach = "Informatik"
  AND SSP.Abschluss = "Bachelor"
GROUP BY S.Pseudonym
HAVING WrittenFirstTerm > 0 -- Ignore entries with no recorded first semester.
ORDER BY WrittenFirstTerm ASC, WrittenSecondTerm ASC
