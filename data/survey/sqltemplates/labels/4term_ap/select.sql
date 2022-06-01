--  Whether the students have passed a sufficient amount of exams
--  (Abschlussprüfungen, AP) after fourth term.
--  Assuming around 20 AP after a successful bachelor, we have ~13.33 AP after
--  fourth term. Giving some room of error, we try to predict who has more than
--  10.
case when SUM(CASE WHEN SSP.Fachsemester <= 4 AND SSP.Status = 'bestanden'
                    THEN 1 ELSE 0 END) >= 10
  then 1 else 0 end as FourthTermAP
