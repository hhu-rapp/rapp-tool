--  Whether the students achieve sufficient credits after four semesters.
--  Sufficient is defined as 100: 30 CP per semester adds up to 120 CP after
--  four semesters. We give 20 CP wiggle room.
case when SUM(CASE WHEN SSP.Fachsemester <= 4 THEN SSP.ECTS ELSE 0 END) >= 100
  then 1 else 0 end as FourthTermCP
