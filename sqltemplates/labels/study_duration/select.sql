-- StudyDuration labels
-- 4: four or less semesters
-- 5/6/7/8/9: five/six/.../nine semesters
-- 10: ten or more semesters
CASE WHEN TermsNeeded.LastTerm <= 4 THEN 4
ELSE CASE WHEN TermsNeeded.LastTerm >= 10 THEN 10
ELSE TermsNeeded.LastTerm END END as StudyDuration
