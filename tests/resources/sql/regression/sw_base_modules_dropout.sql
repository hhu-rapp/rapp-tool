-- Features:
--  Binary markers whether
--  * Erhebungsverfahren I
--  * Erhebungsverfahren II
--  * Basismodul Politikwissenschaften
--  * Basismodul Kommunikations- und Medienwissenschaften
--  * Basismodul Soziologie
--  were passed and how many attempts where needed.
--  Further contains information of the achieved grade.
-- Target variables:
--  Dropout defined as "no exam written in last 3 semesters"
SELECT
  -- S.Geburtsjahr,
  S.Geschlecht,
  S.Deutsch,
  strftime("%Y", E.Immatrikulationsdatum) - S.Geburtsjahr as AlterEinschreibung,
  case when EV_AP.Bestanden IS NOT NULL then EV_AP.Bestanden else 0 end as EV_AP_Bestanden,
  case when EV_AP.Note IS NOT NULL then EV_AP.Note else 5. end as EV_AP_Note,
  case when EV_AP.Versuche IS NOT NULL then EV_AP.Versuche else 0 end as EV_AP_Versuche,
  case when EV2_AP.Bestanden IS NOT NULL then EV2_AP.Bestanden else 0 end as EV2_AP_Bestanden,
  case when EV2_AP.Note IS NOT NULL then EV2_AP.Note else 5. end as EV2_AP_Note,
  case when EV2_AP.Versuche IS NOT NULL then EV2_AP.Versuche else 0 end as EV2_AP_Versuche,
  case when Sozi_AP.Bestanden IS NOT NULL then Sozi_AP.Bestanden else 0 end as Sozi_AP_Bestanden,
  case when Sozi_AP.Note IS NOT NULL then Sozi_AP.Note else 5. end as Sozi_AP_Note,
  case when Sozi_AP.Versuche IS NOT NULL then Sozi_AP.Versuche else 0 end as Sozi_AP_Versuche,
  case when Polit_AP.Bestanden IS NOT NULL then Polit_AP.Bestanden else 0 end as Polit_AP_Bestanden,
  case when Polit_AP.Note IS NOT NULL then Polit_AP.Note else 5. end as Polit_AP_Note,
  case when Polit_AP.Versuche IS NOT NULL then Polit_AP.Versuche else 0 end as Polit_AP_Versuche,
  case when Komm_AP.Bestanden IS NOT NULL then Komm_AP.Bestanden else 0 end as Komm_AP_Bestanden,
  case when Komm_AP.Note IS NOT NULL then Komm_AP.Note else 5. end as Komm_AP_Note,
  case when Komm_AP.Versuche IS NOT NULL then Komm_AP.Versuche else 0 end as Komm_AP_Versuche,
  Dropout.Dropout
FROM
  Student as S,
  Student_schreibt_Pruefung as SSP,
  Pruefung as P,
  Einschreibung as E
LEFT JOIN
  ( SELECT
      max(case when SSP.Status = 'bestanden' then 1 else 0 end) as Bestanden,
      max(SSP.Versuch) as Versuche,
      min(case when SSP.Note is not null and SSP.Note > 0 then SSP.Note else 5.0 end) as Note,
      SSP.Pseudonym
    FROM
      Student_schreibt_Pruefung as SSP,
      Pruefung as P
    WHERE P.Nummer = SSP.Nummer
      AND P.Version = SSP.Version
      AND P.Modul IN ('AP Erhebungsverfahren I (Klausur)', 'Erhebungsverfahren I')
      AND SSP.Fachsemester <= 2
    GROUP BY SSP.Pseudonym
    ) as EV_AP
  ON EV_AP.Pseudonym = SSP.Pseudonym
LEFT JOIN
  ( SELECT
      max(case when SSP.Status = 'bestanden' then 1 else 0 end) as Bestanden,
      max(SSP.Versuch) as Versuche,
      min(case when SSP.Note is not null and SSP.Note > 0 then SSP.Note else 5.0 end) as Note,
      SSP.Pseudonym
    FROM
      Student_schreibt_Pruefung as SSP,
      Pruefung as P
    WHERE P.Nummer = SSP.Nummer
      AND P.Version = SSP.Version
      AND P.Modul IN ('AP Erhebungsverfahren II (Klausur)', 'Erhebungsverfahren II')
      AND SSP.Fachsemester <= 2
    GROUP BY SSP.Pseudonym
    ) as EV2_AP
  ON EV2_AP.Pseudonym = SSP.Pseudonym
LEFT JOIN
  ( SELECT
      max(case when SSP.Status = 'bestanden' then 1 else 0 end) as Bestanden,
      max(SSP.Versuch) as Versuche,
      min(case when SSP.Note is not null and SSP.Note > 0 then SSP.Note else 5.0 end) as Note,
      SSP.Pseudonym
    FROM
      Student_schreibt_Pruefung as SSP,
      Pruefung as P
    WHERE P.Nummer = SSP.Nummer
      AND P.Version = SSP.Version
      AND P.Modul IN ('AP Basismodul Soziologie (Klausur)', 'Soziologie')
      AND SSP.Fachsemester <= 2
    GROUP BY SSP.Pseudonym
    ) as Sozi_AP
  ON Sozi_AP.Pseudonym = SSP.Pseudonym
LEFT JOIN
  ( SELECT
      max(case when SSP.Status = 'bestanden' then 1 else 0 end) as Bestanden,
      max(SSP.Versuch) as Versuche,
      min(case when SSP.Note is not null and SSP.Note > 0 then SSP.Note else 5.0 end) as Note,
      SSP.Pseudonym
    FROM
      Student_schreibt_Pruefung as SSP,
      Pruefung as P
    WHERE P.Nummer = SSP.Nummer
      AND P.Version = SSP.Version
      AND P.Modul IN ('AP Basismodul Politikwissenschaft (Klausur)', 'Politikwissenschaft')
      AND SSP.Fachsemester <= 2
    GROUP BY SSP.Pseudonym
    ) as Polit_AP
  ON Polit_AP.Pseudonym = SSP.Pseudonym
LEFT JOIN
  ( SELECT
      max(case when SSP.Status = 'bestanden' then 1 else 0 end) as Bestanden,
      max(SSP.Versuch) as Versuche,
      min(case when SSP.Note is not null and SSP.Note > 0 then SSP.Note else 5.0 end) as Note,
      SSP.Pseudonym
    FROM
      Student_schreibt_Pruefung as SSP,
      Pruefung as P
    WHERE P.Nummer = SSP.Nummer
      AND P.Version = SSP.Version
      AND P.Modul IN ('AP Basismodul Kommunikations- und Medienwissenschaft (Klausur)',
                      'Kommunikations- und Medienwissenschaft')
      AND SSP.Fachsemester <= 2
    GROUP BY SSP.Pseudonym
    ) as Komm_AP
  ON Komm_AP.Pseudonym = SSP.Pseudonym
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
  AND E.Studienfach = "Sozialwiss.- Medien, Pol."
  AND E.Abschluss like "bachelor%"
  AND SSP.Studienfach = E.Studienfach
  AND SSP.Abschluss = E.Abschluss
  AND Dropout.Studienfach = E.Studienfach
  AND Dropout.Abschluss = E.Abschluss
  -- Make sure we only have students which took part in at least one of these
  AND NOT (EV_AP.Versuche IS NULL
           AND EV2_AP.Versuche IS NULL
           AND Sozi_AP.Versuche IS NULL
           AND Polit_AP.Versuche IS NULL
           AND Komm_AP.Versuche IS NULL
           )
  -- Only consider since PO 2007
  AND '2007-01-01' <= date(E.Immatrikulationsdatum)
  AND Dropout.Dropout IN (0, 1) -- NULL-Entries are sorted out
GROUP BY S.Pseudonym
