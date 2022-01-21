--  RSZ (Regelstudienzeit) - whether the bachelor's is finished after 6 terms
case when TermsNeeded.LastTerm > 6 then 0 else 1 end as RSZ
