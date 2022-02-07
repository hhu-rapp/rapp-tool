import chevron
import os

def save_config_file(studies_id, features_id, labels_id, data, fairness=False):
    if fairness:
        set_name = lambda file: os.path.join(studies_id,features_id,'fairness',file)
    else:
        set_name = lambda file: os.path.join(studies_id,features_id,file)

    file = set_name(f'{studies_id}_{features_id}_{labels_id}.ini')
    os.makedirs(os.path.dirname(file), exist_ok=True)
    with open(file, 'w') as scr:
        scr.write(data)
        scr.close()

# Lists of of values to iterate
filename=['data/rapp.db']
studies_id=['cs','sw']
features_id=['first_term_modules', 'first_term_grades', 'first_term_ects', 'first_term_grades_and_ectp']
labels_id=['3_dropout', '4term_ap', '4term_cp', 'master_admission', 'rsz']
type=['Classification','Regression']
sensitive_attributes=["[Geschlecht, Deutsch]"]
fairness=[True,False]

# labels id for which regression is used for all others classification will be used
regression_id =[]

for database in filename:
    mustache = {'filename': database}

    for studies in studies_id:
        mustache['studies_id']= studies

        for features in features_id:
            mustache['features_id']= features

            for labels in labels_id:
                mustache['labels_id']= labels

                if labels in regression_id:
                    mustache['type']='Regression'
                else:
                    mustache['type']='Classification'

                for fairness_option in fairness:
                    mustache['fairness']=fairness_option

                    if fairness_option:

                        for s_attributes in sensitive_attributes:
                            mustache['sensitive_attributes']=s_attributes

                            with open ("predictions_template.ini", "r") as template:
                                config = chevron.render(template, mustache)
                            template.close()
                            save_config_file(studies, features, labels, config, fairness=True)

                    else:

                        with open ("predictions_template.ini", "r") as template:
                            config = chevron.render(template, mustache)
                            template.close()
                            save_config_file(studies, features, labels, config)
