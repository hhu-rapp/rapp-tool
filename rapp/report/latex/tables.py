
import chevron
import numpy as np

import rapp.resources as rc


def tex_performance_table(estimator, results):
    """
    Translates the results for the given estimator into latex table source code.

    Parameters
    ----------
    estimator : str
        Name of the estimator; will be used in the table header.

    results : dict[str -> dict]
        Dictionary containing the results to display in the table.
        Maps the two training modes 'train', 'test' onto performance measures.
        The following form is expected for each mode:

            {'scores': {'score_fun': float, ...}}

        where score_fun is the name of a scoring function, mapping to the
        respectively measured value.

    Returns
    -------
    tex : str
        Latex table source code.
    """
    # Metrics table
    template = rc.get_text("reports/latex/metrics_table.tex")
    metrics = []
    for m in results["train"]["scores"].keys():
        res = {'name': m,
               'train': f"{results['train']['scores'][m]:.3f}",
               'test': f"{results['test']['scores'][m]:.3f}",
               }
        metrics.append(res)
    mtbl = chevron.render(template, {'metrics': metrics,
                                     'title': estimator,
                                     'label': estimator})
    return mtbl


def tex_cross_validation(estimator, data):
    cv_scores = data

    results = {}
    metrics = [metric[6:] for metric in cv_scores if metric[:6] == "train_"]
    n_folds = len(cv_scores["train_" + metrics[0]])

    # The format we need is the following for each metric.
    # {'title': str,
    #  'fold_ids': [{'id': int}, ...],
    #  'n_folds': int,
    #  'train_col_start': int,
    #  'train_col_end: int,
    #  'test_col_start': int,
    #  'test_col_end: int,
    #  'metrics': [{'name': str,
    #   'train_folds': [{'value': float}, ...],
    #   'test_folds': [{'value': float}, ...],
    #   'train_avg': float,
    #   'train_std': float,
    #   'test_avg': float,
    #   'test_std': float}],
    # }
    mustache = {'title': estimator,
                'fold_ids': [{'id': i} for i in range(n_folds)],
                'metrics': []}
    for metric in metrics:
        mdict = {'name': metric}
        for mode in ["train", "test"]:
            values = [x for x in cv_scores[f"{mode}_{metric}"]]
            value_list = [{'value': str(f'{x:.2f}')} for x in values]
            mdict[f'{mode}_folds'] = value_list

            mdict[f"{mode}_avg"] = str(f"{np.average(values):.2f}")
            mdict[f"{mode}_std"] = str(f"{np.std(values):.2f}")
        mustache['metrics'].append(mdict)

    # Column positions
    n_set_cols = n_folds + 1
    train_start = 2
    test_start = train_start + n_set_cols

    mustache["n_folds"] = n_folds
    mustache["n_set_cols"] = n_set_cols
    mustache["train_col_start"] = train_start
    mustache["train_col_end"] = train_start + n_set_cols - 1
    mustache["test_col_start"] = test_start
    mustache["test_col_end"] = test_start + n_set_cols - 1

    template = rc.get_text("reports/latex/cv_table.tex")
    return chevron.render(template, mustache)


def tex_fairness(estimator, data):
    """
    Translates the fairness evaluation for the given estimator
    into latex table source code.

    Parameters
    ----------
    estimator : str
        Name of the estimator; will be used in the table header.
    data : dict
        Dictionary containing the fairness evaluation results.
        A fairness result has the form

            {protected_attribute:
                {notion_name: {'train': train_results,
                               'test': test_results}},
                 ...}

    Returns
    -------
    tex : str
    """
    fairness = {'title': estimator,
                'groups': [],
                'modes': []}

    # First, we build the info over the groups key, which will look like this:
    #  'groups': [{'group': string,
    #              'subgroups': [{'subgroup': string}, ...],
    #              'has_diff': bool,
    #              'start_column': int,
    #              'end_column': int,
    #              'num_cols': int,
    #              'is_last': bool}]
    # }

    groups = data.keys()
    notions = None  # Filled below.
    next_start = 3  # Two columns in front of first group info.

    for group in groups:
        group_dict = {'group': group}

        if notions is None:
            notions = list(data[group].keys())

        subgroups = data[group][notions[0]]["train"].keys()
        group_dict['subgroups'] = [{'subgroup': sub} for sub in subgroups]
        group_dict['has_diff'] = True  # Diff column is always added

        fairness['groups'].append(group_dict)

        group_dict['start_column'] = next_start
        # We add a difference column. Hence at least three cols.
        num_colums = len(subgroups) + 1
        next_start += num_colums
        group_dict['end_column'] = next_start - 1
        group_dict['num_cols'] = num_colums

    if len(groups) > 0:
        fairness['groups'][-1]['is_last'] = True  # For table formatting.
    if notions is None:
        notions = []  # If no groups are given, value is not set in loop above.

    # For the modes key, we want a list of dictionaries of the following form:
    #  {'mode': string,
    #   'notions': [{'notion': string,
    #                'group_measures': [{
    #                  'group': string,
    #                  'measures': [{'value': double,
    #                                'subgroup': string},
    #                               ...]
    #                  'difference': difference_if_binary}, ...]},
    #   ...]}
    for mode in ["train", "test"]:
        mode_dict = {'mode': mode.capitalize(),
                     'notions': []}
        for notion in notions:
            notion_dict = {'notion': notion,
                           'group_measures': []}
            for group_dict in fairness['groups']:
                group = group_dict['group']
                subgroups = group_dict['subgroups']

                outcomes = data[group][notion][mode]
                # The fairness metric returns a dictionary
                if isinstance(outcomes, dict):
                    measures_dict = {
                        'group': group,
                        'measures': [{'value':
                                      f"{outcomes[sub['subgroup']]['affected_percent']:.3f}" if outcomes.get(sub['subgroup']) is not None else '-',
                                      'subgroup': sub['subgroup']}
                                     for sub in subgroups],
                        'difference': "-" if len(subgroups) != 2 else
                        f"{(abs(outcomes[subgroups[0]['subgroup']]['affected_percent']) - abs(outcomes[subgroups[1]['subgroup']]['affected_percent'])):.3f}"
                    }
                # The fairness metric returns a single value
                if isinstance(outcomes, np.float64):
                    measures_dict = {
                        'group': group,
                        'measures': [{'value':
                                      "-",
                                      'subgroup': sub['subgroup']}
                                     for sub in subgroups],
                        'difference': f"{outcomes:.3f}"
                    }

                notion_dict['group_measures'].append(measures_dict)
            mode_dict['notions'].append(notion_dict)
        fairness["modes"].append(mode_dict)

    fairness['label'] = data.get('label', False)
    tex = rc.get_text("reports/latex/fairness_table.tex")
    tex = chevron.render(tex, fairness)
    return tex


def tex_regression_fairness(estimator, data):
    """
    Translates the fairness evaluation for the given regressor
    into latex table source code.

    Parameters
    ----------
    estimator : str
        Name of the estimator; will be used in the table header.
    data : dict
        Dictionary containing the fairness evaluation results.
        A fairness result has the form

            {protected_attribute:
                {notion_name: {'train': train_results,
                               'test': test_results}},
                 ...}

    Returns
    -------
    tex : str
    """
    fairness = {'title': estimator,
                'modes': [],
                'groups': []}
    groups = [g for g in data]
    fairness['groups'] = [{'group': g} for g in groups]

    if len(groups) > 0:
        # Todo: Does it even make sense to have no groups?
        notions = list(data[groups[0]].keys())
    else:
        notions = []

    # For the modes key, we want a list of dictionaries of the following form:
    #  {'mode': string,
    #   'notions': [{'notion': string,
    #                'group_measures': [{
    #                  'group': string,
    #                  'outcome': float}, ...]},
    #   ...]}
    for mode in ["train", "test"]:
        mode_dict = {'mode': mode.capitalize(),
                     'notions': []}
        for notion in notions:
            notion_dict = {'notion': notion,
                           'group_measures': []}
            for group in groups:

                outcome = data[group][notion][mode]
                measures_dict = {
                    'group': group,
                    'outcome': f"{outcome:.3f}"
                }

                notion_dict['group_measures'].append(measures_dict)
            mode_dict['notions'].append(notion_dict)
        fairness["modes"].append(mode_dict)

    # Mark last mode.
    fairness['modes'][-1]['is_last'] = True

    fairness['label'] = estimator
    tex = rc.get_text("reports/latex/fairness_regressor_table.tex")
    tex = chevron.render(tex, fairness)
    return tex
