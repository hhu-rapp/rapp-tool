#!/bin/bash
subjects=("cs" "sw")
features=("first_term_ects" "first_term_grades" "first_term_grades_and_ectp"
          "first_term_modules" "second_term_base_modules")
labels=("3_dropout" "4term_ap" "4term_cp" "master_admission" "rsz" "study_duration")

for s in "${subjects[@]}"
do
  for f in "${features[@]}"
  do
    for l in "${labels[@]}"
    do
      if [ -d "sqltemplates/features/${s}_${f}" ]; then
        exp="${s}/${f}/${l}"
        echo "running $exp"
        python -m rapp -cf settings/tests/experiments.ini -sid $s -fid $f -lid $l \
                      --report_path reports/exp/$exp
      fi
    done
  done
done
