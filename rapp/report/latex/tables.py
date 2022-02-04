
import chevron

import rapp.report.resources as rc


def tex_performance_deprecated(estimator, results):
    # Metrics table
    mtbl = rc.get_text("metrics_table.tex")
    metrics = []
    for m in results["CV"]["avg_scores"].keys():
        res = {'name': m,
               'cv': f"{results['CV']['avg_scores'][m]:.3f}",
               }
        metrics.append(res)
    mtbl = chevron.render(mtbl, {'metrics': metrics,
                                 'title': estimator,
                                 'label': results.get('label', False)})
    return mtbl

def tex_performance(estimator, results):
    # Metrics table
    template = rc.get_text("metrics_table.tex")

    cv_tables=[]
    for cv in results["CV"]["scores"].keys():
        metrics = []

        for m in results["CV"]["scores"][cv]['train'].keys():
            res = {'name': m,
                    'train': f"{results['CV']['scores'][cv]['train'][m]:.3f}",
                    'test': f"{results['CV']['scores'][cv]['test'][m]:.3f}",
                    }

            metrics.append(res)
        # id refers to the cross validation id for the estimator
        cv_mtbl = chevron.render(template, {'id': cv,
                                'metrics': metrics,
                                 'title': estimator,
                                 'label': results.get('label', False)})

        cv_tables.append(cv_mtbl)
    mtbl = "\n".join(cv_tables)
    return mtbl

def tex_fairness(estimator, data):
    fairness = {'title': estimator,
                'groups': [],
                'modes': []}

    # Building a dictionary of the following form
    # {'title': estimator_name,
    #  'modes': [{'mode': string,
    #             'notions': [{'notion': string,
    #                          'group_measures': [{
    #                            'group': string,
    #                            'measures': [{'value': double,
    #                                          'subgroup': string},
    #                                         ...]
    #                            'difference': difference_if_binary}, ...]},
    #             ...]}, ...],
    #  'groups': [{'group': string,
    #              'subgroups': [{'subgroup': string}, ...],
    #              'has_diff': bool,
    #              'start_column': int,
    #              'end_column': int,
    #              'num_cols': int,
    #              'is_last': bool}]
    # }

    groups = data["CV"]["fairness"].keys()
    notions = None  # Filled below.
    next_start = 3  # Two columns in front of first group info.
    for group in groups:
        group_dict = {'group': group}

        if notions is None:
            notions = list(data["CV"]["fairness"][group].keys())

        subgroups = data["CV"]["fairness"][group][notions[0]
                                                     ]["outcomes"].keys()
        group_dict['subgroups'] = [{'subgroup': sub} for sub in subgroups]
        group_dict['has_diff'] = (len(subgroups) == 2)

        fairness['groups'].append(group_dict)

        group_dict['start_column'] = next_start
        # If binary, we add a difference column. Hence at least three cols.
        num_colums = max(len(subgroups), 3)
        next_start += num_colums
        group_dict['end_column'] = next_start - 1
        group_dict['num_cols'] = num_colums
    if len(groups) > 0:
        fairness['groups'][-1]['is_last'] = True
    if notions is None:
        notions = []  # If no groups are given, value is not set in loop above.

    for mode in ['Dataset']:
        mode_dict = {'mode': mode.capitalize(),
                     'notions': []}
        for notion in notions:
            notion_dict = {'notion': notion,
                           'group_measures': []}
            for group_dict in fairness['groups']:
                group = group_dict['group']
                subgroups = group_dict['subgroups']

                outcomes = data["CV"]["fairness"][group][notion]["outcomes"]
                measures_dict = {
                    'group': group,
                    'measures': [{'value':
                                  f"{outcomes[sub['subgroup']]['affected_percent']:.3f}",
                                  'subgroup': sub['subgroup']}
                                 for sub in subgroups],
                    'difference': "-" if len(subgroups) != 2 else
                    f"{(abs(outcomes[subgroups[0]['subgroup']]['affected_percent']) - abs(outcomes[subgroups[1]['subgroup']]['affected_percent'])):.3f}"

                }

                notion_dict['group_measures'].append(measures_dict)
            mode_dict['notions'].append(notion_dict)
        fairness["modes"].append(mode_dict)

    fairness['label'] = data.get('label', False)
    tex = rc.get_text("fairness_table.tex")
    tex = chevron.render(tex, fairness)
    return tex
