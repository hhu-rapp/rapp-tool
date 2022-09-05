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
case when Ana.Versuche IS NOT NULL then Ana.Versuche else 0 end as AnaVersuche
