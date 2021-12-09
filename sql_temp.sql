SELECT S.Geburtsjahr, S.Geschlecht,
CASE WHEN S.Deutsch = 1 THEN 'ja' ELSE 'nein' END as Deutsch, COUNT(SSP.Nummer) as ExamsWritten,
COUNT(CASE WHEN SSP.Status LIKE '%nicht bestanden%' THEN 1 ELSE null END) ExamsFailed,
AVG(CASE WHEN SSP.Note != 0.0 or SSP.Note != null THEN SSP.Note ELSE null END) as AvgGrade,
SUM(SSP.ECTS) as ECTS
FROM Student as S, Student_schreibt_Pruefung as SSP, Pruefung as P, Einschreibung as E
WHERE S.Pseudonym = SSP.Pseudonym
AND S.Pseudonym = E.Pseudonym
AND SSP.Version = P.Version
AND SSP.Nummer = P.Nummer
AND SSP.Hochschulsemester == 1
AND SSP.Fachsemester == 1
AND E.Studienfach = "Informatik"
AND SSP.Abschluss = "Bachelor"
GROUP BY S.Pseudonym, S.Geburtsjahr, S.Geschlecht, S.Deutsch
ORDER BY ECTS DESC