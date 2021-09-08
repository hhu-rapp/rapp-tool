-- Features:
--  Binary markers whether Linear Algebra, Programming (Info 1), and
--  Algorithms (Info 3) where passed and how many attempts where used.
--  Last achieved grade in Programming and Algorithms. Linear Algebra does not
--  have any recorded grades for CS students besides 0.0 (passed) and 5.0
--  (failed).
-- Target variables:
--  Number of credits in fourth term
-- Note:
--  In 2018 PO computer science switched what the first term modules are for
--  students, and to be more relevant for future data, we consider these new
--  three here: linear algebra, programming, and algorithms
SELECT
  S.Geburtsjahr,
  S.Geschlecht,
  S.Deutsch,
  SSP.Pseudonym,
  case when LA.Bestanden IS NOT NULL then LA.Bestanden else 0 end as LABestanden,
  case when LA.Versuche IS NOT NULL then LA.Versuche else 0 end as LAVersuche,
  case when Prog.Bestanden IS NOT NULL then Prog.Bestanden else 0 end as ProgBestanden,
  case when Prog.Versuche IS NOT NULL then Prog.Versuche else 0 end as ProgVersuche,
  case when ProgNote.Note IS NOT NULL then ProgNote.Note else 5. end as ProgNote,
  case when Algo.Bestanden IS NOT NULL then Algo.Bestanden else 0 end as AlgoBestanden,
  case when Algo.Versuche IS NOT NULL then Algo.Versuche else 0 end as AlgoVersuche,
  case when AlgoNote.Note IS NOT NULL then AlgoNote.Note else 5. end as AlgoNote,
  SUM(CASE WHEN SSP.Fachsemester <= 4 THEN SSP.ECTS ELSE 0 END) as FourthTermCP
  -- SUM(CASE WHEN SSP.Fachsemester <= 6 THEN SSP.ECTS ELSE 0 END) as SixthTermCP
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
      AND P.Modul IN ('Algorithmen und Datenstrukturen', 'Grundlagen der Algorithmen und Datenstrukturen')
    GROUP BY SSP.Pseudonym
    ) as Algo
  ON Algo.Pseudonym = SSP.Pseudonym
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
      AND P.Modul IN ('Algorithmen und Datenstrukturen', 'Grundlagen der Algorithmen und Datenstrukturen')
    ORDER BY SSP.Pseudonym
    ) as AlgoNote
  ON Algo.Pseudonym = AlgoNote.Pseudonym AND Algo.Versuche = AlgoNote.Versuch
WHERE S.Pseudonym = SSP.Pseudonym
  AND S.Pseudonym = E.Pseudonym
  AND SSP.Version = P.Version
  AND SSP.Nummer = P.Nummer
  AND E.Studienfach = "Informatik"
  AND E.Abschluss = "Bachelor"
  AND SSP.Studienfach = "Informatik"
  AND SSP.Abschluss = "Bachelor"
  -- Make sure we only have students which took part in at least one of these
  AND NOT (LA.Versuche IS NULL AND Prog.Versuche IS NULL AND Algo.Versuche IS NULL)
  -- Need People who are enrolled since at least 4 semesters
  AND '2019-04-01' >= date(E.Immatrikulationsdatum)
  -- Only consider since PO 2007
  AND '2007-01-01' <= date(E.Immatrikulationsdatum)
GROUP BY S.Pseudonym
