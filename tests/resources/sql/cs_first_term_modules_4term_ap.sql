SELECT
-- Features
--  Binary markers whether Linear Algebra, Programming (Info 1), and
--  Analysis were passed and how many attempts were used.
--  Last achieved grade in Programming. Linear Algebra and Analysis do not
--  have any recorded grades for CS students besides 0.0 (passed?) and 5.0
--  (failed).
--
-- Note:
--  In 2018 PO computer science switched what the first term modules are for
--  students, and to be more relevant for future data, we consider these new
--  three here: linear algebra, programming, and algorithms
--
-- protected attributes
-- S.Geburtsjahr,
S.Geschlecht,
S.Deutsch,
strftime("%Y", E.Immatrikulationsdatum) - S.Geburtsjahr as AlterEinschreibung,
--
case when LA.Bestanden IS NOT NULL then LA.Bestanden else 0 end as LABestanden,
case when LA.Versuche IS NOT NULL then LA.Versuche else 0 end as LAVersuche,
case when Prog.Bestanden IS NOT NULL then Prog.Bestanden else 0 end as ProgBestanden,
case when Prog.Versuche IS NOT NULL then Prog.Versuche else 0 end as ProgVersuche,
case when ProgNote.Note IS NOT NULL then ProgNote.Note else 5. end as ProgNote,
case when Ana.Bestanden IS NOT NULL then Ana.Bestanden else 0 end as AnaBestanden,
case when Ana.Versuche IS NOT NULL then Ana.Versuche else 0 end as AnaVersuche,
-- Labels
--  Whether the students have passed a sufficient amount of exams
--  (Abschlussprüfungen, AP) after fourth term.
--  Assuming around 20 AP after a successful bachelor, we have ~13.33 AP after
--  fourth term. Giving some room of error, we try to predict who has more than
--  10.
case when SUM(CASE WHEN SSP.Fachsemester <= 4 AND SSP.Status = 'bestanden'
                    THEN 1 ELSE 0 END) >= 10
  then 1 else 0 end as FourthTermAP
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

WHERE
    S.Pseudonym = SSP.Pseudonym
AND S.Pseudonym = E.Pseudonym
AND SSP.Version = P.Version
AND SSP.Nummer = P.Nummer
AND E.Studienfach = "Informatik"
AND E.Abschluss = "Bachelor"
AND SSP.Studienfach = E.Studienfach
AND SSP.Abschluss = E.Abschluss
-- Make sure we only have students which took part in at least one of these
AND NOT (LA.Versuche IS NULL AND Prog.Versuche IS NULL AND Ana.Versuche IS NULL)
-- Only consider since PO 2007
AND '2007-01-01' <= date(E.Immatrikulationsdatum)

GROUP BY S.Pseudonym
