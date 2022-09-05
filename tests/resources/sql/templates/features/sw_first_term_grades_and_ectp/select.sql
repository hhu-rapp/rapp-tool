--
--
-- protected attributes
S.Geschlecht,
S.Deutsch,
strftime("%Y", E.Immatrikulationsdatum) - S.Geburtsjahr as AlterEinschreibung,
--
FirstTermData.Ectp,
FirstTermData.KlausurenGeschrieben,
FirstTermData.KlausurenBestanden,
FirstTermData.KlausurenNichtBestanden,
CASE WHEN FirstTermData.DurchschnittsNoteBestanden IS NULL
     then 5 else FirstTermData.DurchschnittsNoteBestanden end as DurchschnittsnoteBestanden,
CASE WHEN FirstTermData.DurchschnittsNoteTotal IS NULL
     then 5 else FirstTermData.DurchschnittsNoteTotal end as DurchschnittsnoteTotal,
CASE WHEN FirstTermData.DurchschnittsNoteBestanden IS NULL
     then 0 else
  (SUM(CASE WHEN SSP.Note <> 0 AND SSP.Status = 'bestanden'
      THEN (SSP.NOTE-FirstTermData.DurchschnittsNoteBestanden)*(SSP.NOTE-FirstTermData.DurchschnittsNoteBestanden)
      ELSE NULL END)
    / FirstTermData.KlausurenBestanden)
END as VarianzNoteBestanden,
CASE WHEN FirstTermData.DurchschnittsNoteTotal IS NULL
     then 0 else
  (SUM ((SSP.NOTE-FirstTermData.DurchschnittsNoteTotal)
        * (SSP.NOTE-FirstTermData.DurchschnittsNoteTotal))
    / FirstTermData.KlausurenGeschrieben)
END as VarianzNoteTotal,
-- Ratio of passed exams; zero if none attempted.
CASE WHEN COUNT(CASE WHEN SSP.Fachsemester = 1 THEN SSP.Pseudonym ELSE null END) = 0
     THEN 0.0
     ELSE (
       COUNT(CASE WHEN SSP.Fachsemester = 1 AND SSP.Status = 'bestanden'
             THEN SSP.Pseudonym ELSE null END )
       * 1. / COUNT(CASE WHEN SSP.Fachsemester = 1 THEN SSP.Pseudonym ELSE null END)
     )
     END as PassedExamsRatio,
IFNULL(FirstTermData.Ectp*1./FirstTermData.KlausurenGeschrieben,
       0) as EctpPerExam
