-- Whether master admission will be achieved or not
case when FinalGrade.Grade <= 2.5 then 1 else 0 end as MasterZulassung
