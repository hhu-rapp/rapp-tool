SELECT
-- Features
{{feature_select}},
-- Labels
{{label_select}}
FROM
  Student as S,
  Student_schreibt_Pruefung as SSP,
  Pruefung as P,
  Einschreibung as E
{{feature_joins}}
{{label_joins}}
WHERE
    S.Pseudonym = SSP.Pseudonym
AND S.Pseudonym = E.Pseudonym
AND SSP.Version = P.Version
AND SSP.Nummer = P.Nummer
{{feature_where}}
{{label_where}}
GROUP BY S.Pseudonym
