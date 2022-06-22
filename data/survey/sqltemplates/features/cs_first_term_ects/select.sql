--
--
-- protected attributes
S.Geschlecht,
S.Staatsangehoerigkeit,
strftime("%Y", E.Immatrikulationsdatum) - S.Geburtsjahr as AlterEinschreibung,
--
SUM(CASE WHEN SSP.Fachsemester = 1 THEN SSP.ECTS ELSE 0 END) as EctsFirstTerm,
COUNT(CASE WHEN SSP.Fachsemester = 1 THEN SSP.Pseudonym ELSE null END ) as ExamsFirstTerm,
COUNT(CASE WHEN SSP.Fachsemester = 1 AND SSP.Status = 'bestanden'
           THEN SSP.Pseudonym ELSE null END ) as PassedFirstTerm,
COUNT(CASE WHEN SSP.Fachsemester = 1 AND SSP.Status <> 'bestanden'
           THEN SSP.Pseudonym ELSE null END ) as FailedFirstTerm,
-- Ratio of passed exams; zero if none attempted.
CASE WHEN COUNT(CASE WHEN SSP.Fachsemester = 1 THEN SSP.Pseudonym ELSE null END) = 0
     THEN 0.0
     ELSE (
       COUNT(CASE WHEN SSP.Fachsemester = 1 AND SSP.Status = 'bestanden'
             THEN SSP.Pseudonym ELSE null END )
       * 1. / COUNT(CASE WHEN SSP.Fachsemester = 1 THEN SSP.Pseudonym ELSE null END)
     )
     END as PassedExamsRatio,
IFNULL(SUM(CASE WHEN SSP.Fachsemester = 1 THEN SSP.ECTS ELSE 0 END) * 1.
        / COUNT(CASE WHEN SSP.Fachsemester = 1 THEN SSP.Pseudonym ELSE null END),
       0)
  as EctsPerExam
