-- Features:
--  Binary markers whether Linear Algebra, Programming (Info 1), and
--  Analysis were passed and how many attempts were used.
--  Last achieved grade in Programming. Linear Algebra and Analysis do not
--  have any recorded grades for CS students besides 0.0 (passed?) and 5.0
--  (failed).
-- Target variables:
--  RSZ (Regelstudienzeit) - whether the bachelor's is finished after 6 terms
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
  case when TermsNeeded.LastTerm > 6 then 0 else 1 end as RSZ
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
WHERE S.Pseudonym = SSP.Pseudonym
  AND S.Pseudonym = E.Pseudonym
  AND SSP.Version = P.Version
  AND SSP.Nummer = P.Nummer
  AND E.Studienfach = "Informatik"
  AND E.Abschluss = "Bachelor"
  AND SSP.Studienfach = E.Studienfach
  AND SSP.Abschluss = E.Abschluss
  AND TermsNeeded.Pseudonym = E.Pseudonym
  AND TermsNeeded.Studienfach = E.Studienfach
  AND TermsNeeded.Abschluss = E.Abschluss
  -- Only consider since PO 2007
  AND '2007-01-01' <= date(E.Immatrikulationsdatum)
GROUP BY S.Pseudonym
