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
