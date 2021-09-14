-- Features:
--  Binary markers whether
--  * Erhebungsverfahren I
--  * Basismodul Politikwissenschaften
--  * Basismodul Kommunikations- und Medienwissenschaften
--  were passed and how many attempts were used.
-- Target variables:
--  Dropout defined as "no exam written in last 3 semesters"
SELECT
  S.Geburtsjahr,
  S.Geschlecht,
  S.Deutsch,
  strftime("%Y", E.Immatrikulationsdatum) - S.Geburtsjahr as AlterEinschreibung,
  case when EV.Bestanden IS NOT NULL then EV.Bestanden else 0 end as EVBestanden,
  case when EV.Versuche IS NOT NULL then EV.Versuche else 0 end as EVVersuche,
  case when EVNote.Note IS NOT NULL then EVNote.Note else 5. end as EVNote,
  case when Polit.Bestanden IS NOT NULL then Polit.Bestanden else 0 end as PolitBestanden,
  case when Polit.Versuche IS NOT NULL then Polit.Versuche else 0 end as PolitVersuche,
  case when PolitNote.Note IS NOT NULL then PolitNote.Note else 5. end as PolitNote,
  case when Sozi.Bestanden IS NOT NULL then Sozi.Bestanden else 0 end as SoziBestanden,
  case when Sozi.Versuche IS NOT NULL then Sozi.Versuche else 0 end as SoziVersuche,
  case when SoziNote.Note IS NOT NULL then SoziNote.Note else 5. end as SoziNote,
  case when Medien.Bestanden IS NOT NULL then Medien.Bestanden else 0 end as MedienBestanden,
  case when Medien.Versuche IS NOT NULL then Medien.Versuche else 0 end as MedienVersuche,
  case when MedienNote.Note IS NOT NULL then MedienNote.Note else 5. end as MedienNote,
  Dropout.Dropout
FROM
  Student as S,
  Student_schreibt_Pruefung as SSP,
  Pruefung as P,
  Einschreibung as E
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
      AND P.Modul IN ('Erhebungsverfahren I', 'AP Erhebungsverfahren I (Klausur)')
    GROUP BY SSP.Pseudonym
    ) as EV
  ON EV.Pseudonym = SSP.Pseudonym
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
      AND P.Modul IN ('Erhebungsverfahren I', 'AP Erhebungsverfahren I (Klausur)')
    ORDER BY SSP.Pseudonym
    ) as EVNote
  ON EV.Pseudonym = EVNote.Pseudonym AND EV.Versuche = EVNote.Versuch
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
      AND P.Modul IN ('AP Basismodul Politikwissenschaft (Klausur)', 'Politikwissenschaft')
    GROUP BY SSP.Pseudonym
    ) as Polit
  ON Polit.Pseudonym = SSP.Pseudonym
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
      AND P.Modul IN ('AP Basismodul Politikwissenschaft (Klausur)', 'Politikwissenschaft')
    ORDER BY SSP.Pseudonym
    ) as PolitNote
  ON Polit.Pseudonym = PolitNote.Pseudonym AND Polit.Versuche = PolitNote.Versuch
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
      AND P.Modul IN ('AP Basismodul Soziologie (Klausur)', 'Soziologie')
    GROUP BY SSP.Pseudonym
    ) as Sozi
  ON Sozi.Pseudonym = SSP.Pseudonym
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
      AND P.Modul IN ('AP Basismodul Soziologie (Klausur)', 'Soziologie')
    ORDER BY SSP.Pseudonym
    ) as SoziNote
  ON Sozi.Pseudonym = SoziNote.Pseudonym AND Sozi.Versuche = SoziNote.Versuch
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
      -- Note: I don't know if we are missing "Medien- und Kommunikation"
      AND P.Modul IN ('AP Basismodul Kommunikations- und Medienwissenschaft (Klausur)', 'Kommunikations- und Medienwissenschaft')
    GROUP BY SSP.Pseudonym
    ) as Medien
  ON Medien.Pseudonym = SSP.Pseudonym
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
      AND P.Modul IN ('AP Basismodul Kommunikations- und Medienwissenschaft (Klausur)', 'Kommunikations- und Medienwissenschaft')
    ORDER BY SSP.Pseudonym
    ) as MedienNote
  ON Medien.Pseudonym = MedienNote.Pseudonym AND Medien.Versuche = MedienNote.Versuch
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
  AND E.Studienfach in ("Sozialwiss.- Medien, Pol.", "Sozialwissenschaften")
  AND E.Abschluss like "bachelor%"
  AND SSP.Studienfach = E.Studienfach
  AND SSP.Abschluss = E.Abschluss
  AND Dropout.Studienfach = E.Studienfach
  AND Dropout.Abschluss = E.Abschluss
  -- Make sure we only have students which took part in at least one of these
  AND NOT (EV.Versuche IS NULL AND Polit.Versuche IS NULL
           AND Sozi.Versuche IS NULL AND Medien.Versuche IS NULL)
  -- Only consider since PO 2007
  AND '2007-01-01' <= date(E.Immatrikulationsdatum)
  AND Dropout.Dropout IN (0, 1) -- NULL-Entries are sorted out
GROUP BY S.Pseudonym
