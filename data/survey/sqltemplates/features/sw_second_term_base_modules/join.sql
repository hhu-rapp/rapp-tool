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
