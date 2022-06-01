--  Binary markers whether
--  * Erhebungsverfahren I
--  * Erhebungsverfahren II
--  * Basismodul Politikwissenschaften
--  * Basismodul Kommunikations- und Medienwissenschaften
--  * Basismodul Soziologie
--  were passed and how many attempts where needed.
--  Further contains information of the achieved grade.
-- protected attributes
-- S.Geburtsjahr,
S.Geschlecht,
S.Deutsch,
strftime("%Y", E.Immatrikulationsdatum) - S.Geburtsjahr as AlterEinschreibung,
--
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
case when Komm_AP.Versuche IS NOT NULL then Komm_AP.Versuche else 0 end as Komm_AP_Versuche
