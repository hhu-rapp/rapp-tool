import chevron
import numpy as np

import rapp.resources as rc
from rapp.fair.metanotion import max_difference

from rapp.util import estimator_name
from rapp.pipeline import Pipeline

from rapp.report.latex.tables import (
    tex_cross_validation,
    tex_fairness,
    tex_performance_table,
    tex_regression_fairness,
)
from rapp.report.latex.additionalmodels import tex_additional_models


def tex_dataset_report(report):
    """
    Parameters
    ----------
    report : dict[mode -> statistics]
        Dictionary with mode as key which map onto calculated statistics
        over a dataset.
        The statistics are assumed to be in the following format:

            {'groups':
                {group1: {subgroup1: {'total': int,
                                      'outcomes': {label1: int,
                                                   label2: int,
                                                   ...}},
                          subgroup2: {...},
                          ...},
                 group2: {...},
                 ...},
             'outcomes': {label1: int, label2: int, ...},
             'total': int}

    Returns
    -------
    tex : str
        Table displaying the classification statistics of the dataset.
    """

    # Tex file expects the following format for Chevron per mode
    # {'total': int,
    #  'groups: list({'group_name': str,
    #                 'group_size': int,
    #                 'start_column': int,
    #                 'end_column': int,
    #                 'subgroups': list({'sub_name': str, 'sub_count': int})}),
    #  'labels': list({'label': any,
    #                  'label_total': int,
    #                  'label_groups': list({
    #                    'label_group_total': int,
    #                    'label_subgroups': list({
    #                      'label_sub_name': string,
    #                      'label_sub_count})})})}

    mustache = {'modes': []}
    for mode in report:
        dataset = report[mode]

        # Fill in the group names
        groups = []
        start_col_counter = 2
        for group in dataset["groups"]:
            group_data = {'group_name': group,
                          'subgroups': []}
            for sub in dataset["groups"][group].keys():
                sub_data = {
                    "sub_name": sub,
                    "sub_count": dataset["groups"][group][sub]["total"]
                }
                group_data["subgroups"].append(sub_data)
            group_data["size"] = len(group_data["subgroups"])
            group_data["start_column"] = start_col_counter
            group_data["end_column"] = start_col_counter + \
                group_data["size"] - 1
            start_col_counter = group_data["end_column"] + 1
            groups.append(group_data)

        # Fill the label data
        labels = []
        for label in dataset["outcomes"]:
            label = label
            label_data = {'label': label,
                          'label_total': dataset["outcomes"][label],
                          'label_groups': []}
            for group_data in groups:
                group = group_data["group_name"]
                label_group_data = {
                    'label_group_total': 0,
                    'label_subgroups': []}
                for sub_data in group_data["subgroups"]:
                    sub = sub_data['sub_name']
                    sub_count = dataset["groups"][group][sub]["outcomes"][label]
                    label_group_data["label_group_total"] += sub_count
                    label_sub_data = {
                        'label_sub_name': sub,
                        'label_sub_count': sub_count,
                    }
                    label_group_data["label_subgroups"].append(label_sub_data)
                label_data["label_groups"].append(label_group_data)
            labels.append(label_data)

        mode_data = {"mode": mode.capitalize(),
                     "total": dataset["total"],
                     "groups": groups,
                     "labels": labels}
        mustache["modes"].append(mode_data)

    template = rc.get_text("reports/latex/dataset_table.tex")
    tex = chevron.render(template, mustache)
    return tex


def tex_dataset_plot(report):
    """
    Parameters
    ----------
    report : dict[mode -> statistics]
        Dictionary with mode as key which map onto calculated statistics
        over a dataset.
        The statistics are assumed to be in the following format:

            {'groups':
                {group1: {subgroup1: {'total': int,
                                      'outcomes': np.array,
                          subgroup2: {...},
                          ...},
                 group2: {...},
                 ...},
             'outcomes': np.array,
             'total': int}

    Returns
    -------
    tex : str
        Histogram displaying the regression statistics of the dataset.
    """

    # Tex file expects the following format for Chevron per mode
    # {'total': int,
    #  'groups': list({'group_name': str,
    #                  'subgroups': list({'sub_name': str,
    #                                      'sub_count': int,
    #                                      'sub_labels': list({'sub_label': any}, ...)}, ...)}, ...),
    #  'labels': list({'label': any}, ...)}

    mustache = {'modes': []}
    for mode in report:
        dataset = report[mode]

        # Fill in the group names
        groups = []
        for group in dataset["groups"]:
            group_data = {'group_name': group,
                          'subgroups': []}
            for sub in dataset["groups"][group]:
                sub_data = {
                    "sub_name": sub,
                    "sub_count": dataset["groups"][group][sub]["total"]
                }
                single_sub_labels = []
                for sub_label in dataset["groups"][group][sub]["outcomes"]:
                    single_sub_labels.append({"sub_label": sub_label})

                sub_data["sub_labels"] = single_sub_labels
                group_data["subgroups"].append(sub_data)
            groups.append(group_data)

        # Fill the label data
        single_labels = []
        for label in dataset["outcomes"]:
            single_labels.append({"label": label})

        mode_data = {"mode": mode.capitalize(),
                     "total": dataset["total"],
                     "groups": groups,
                     "labels": single_labels}
        mustache["modes"].append(mode_data)

    template = rc.get_text("reports/latex/dataset_plots.tex")
    tex = chevron.render(template, mustache)
    return tex


def tex_performance_overview(performance_results):
    """
    Parameters
    ----------
    performance_results : dict[estimator -> results]
        Dictionary with estimators as key which map onto possibly
        calculated performance results.

        A performance result has the form

            {mode:
                {'scores': {score_functions_results},
                'confusion_matrix' : confusion_matrix_results}}

    Returns
    -------
    tex : str
        Tables displaying the performance of the trained models.
    """

    # Tex file expects the following format for Chevron
    # {'type': string,
    #  'modes: list({'mode': str,
    #                 'metrics': list({'metric': str}),
    #                 'models': list({'model_name': str, 'measures': list({'value': float})})})}

    mustache = {'type': 'Performance',
                'modes': []}

    trained_models = list(performance_results.keys())

    for mode in performance_results[trained_models[0]]:
        metrics = list(performance_results[trained_models[0]][mode]['scores'].keys())

        models = []
        # Fill in the model names
        for model in trained_models:
            model_name = estimator_name(model)

            # Fill the performance metric data
            measures = []
            for metric in metrics:
                measures_dict = {'value': f"{performance_results[model][mode]['scores'][metric]:.3f}"}
                measures.append(measures_dict)

            model_data = {"model_name": model_name,
                         "measures": measures}

            models.append(model_data)

        mode_data = {"mode": mode.capitalize(),
                     "metrics": [{'metric': metric} for metric in metrics],
                     "models": models}

        mustache["modes"].append(mode_data)

    template = rc.get_text("reports/latex/metrics_overview_table.tex")
    tex = chevron.render(template, mustache)

    return tex


def tex_fairness_overview(fairness_results):
    """
    Parameters
    ----------
    fairness_results : dict[estimator -> results]
        Dictionary with estimators as key which map onto possibly
        calculated fairness results.

        A fairness result has the form

            {protected_attribute:
                {notion_name: {'train': train_results,
                               'test': test_results}},
                 ...}

    Returns
    -------
    tex : str
        Tables displaying the Max. (Un)Fairness of the trained models.
    """

    # Tex file expects the following format for Chevron
    # {'type': string,
    #  'modes: list({'mode': str,
    #                 'metrics': list({'metric': str}),
    #                 'models': list({'model_name': str, 'measures': list({'value': float})})})}

    mustache = {'type': 'Max. (Un)Fairness',
                'modes': []}

    trained_models = list(fairness_results.keys())
    sensitive_attributes = list(fairness_results[trained_models[0]].keys())

    for mode in ['train', 'test']:
        metrics = list(fairness_results[trained_models[0]][sensitive_attributes[0]].keys())

        models = []
        # Fill in the model names
        for model in trained_models:
            model_name = estimator_name(model)
            measures = []
            for metric in metrics:

                fairness = []
                for sensitive_attribute in sensitive_attributes:
                    values = fairness_results[model][sensitive_attribute][metric][mode]

                    if type(values) == dict:
                        # Difference across sensitive attribute
                        keys = list(values.keys())
                        group_values = [values[k]["affected_percent"] for k in keys]
                        if len(values) == 2:
                            fairness.append(abs(group_values[0] - group_values[1]))
                        elif len(values) > 2:
                            # We have multiple groups, so we assume the
                            # maximum difference across groups as the final
                            # measure
                            fairness.append(max_difference(group_values))

                    # The fairness metric returns a single value
                    elif type(values) == np.float64:
                        fairness.append(values)
                # Max unfairness across all sensitive attributes
                max_fairness = max(fairness)

                measures_dict = {'value': f"{max_fairness:.3f}"}
                measures.append(measures_dict)

            model_data = {"model_name": model_name,
                         "measures": measures}

            models.append(model_data)

        mode_data = {"mode": mode.capitalize(),
                     "metrics": [{'metric': metric} for metric in metrics],
                     "models": models}

        mustache["modes"].append(mode_data)

    template = rc.get_text("reports/latex/metrics_overview_table.tex")
    tex = chevron.render(template, mustache)

    return tex


def tex_regression_report(pipeline: Pipeline):
    """
    Prepares tex file for a regression report.

    Parameters
    ----------
    pipeline : rapp.pipeline.Pipeline instance
        Pipeline to create the report for.

    Returns
    -------
    tex : str
        Report of the pipeline in tex format.
    """
    return _tex_report_with_functions(
        pipeline,
        dataset_tex_fun=tex_dataset_plot,
        performance_tex_fun=tex_performance_table,
        fairness_tex_fun=tex_regression_fairness,
        cross_validation_tex_fun=tex_cross_validation)


def tex_classification_report(pipeline: Pipeline):
    """
    Prepares tex file for a classification report.

    Parameters
    ----------
    pipeline : rapp.pipeline.Pipeline instance
        Pipeline to create the report for.

    Returns
    -------
    tex : str
        Report of the pipeline in tex format.
    """
    return _tex_report_with_functions(pipeline)


def _tex_report_with_functions(pipeline: Pipeline,
                               dataset_tex_fun=tex_dataset_report,
                               performance_tex_fun=tex_performance_table,
                               fairness_tex_fun=tex_fairness,
                               cross_validation_tex_fun=tex_cross_validation):
    """
    Unified function for tex report creation.
    Can be used by both classification and regression reports to utilise a
    common code logic.

    Parameters
    ----------
    pipeline : rapp.pipeline.Pipeline
        Pipeline to create the report for.
    dataset_tex_fun : function(pipeline: Pipeline) -> str, default: rapp.report.latex.tex_dataset_report
        Function to report dataset metrics.
    performance_tex_fun : function(estimator_name: str, results: dict) -> str, default: rapp.report.latex.tex_performance_table
        Function to report performance metrics.
    fairness_tex_fun : function(estimator_name: str, results: dict) -> str, default: rapp.report.latex.tex_fairness
        Function to report fairness metrics.
    cross_validation_tex_fun : function(estimator_name: str, results: dict) -> str, default: rapp.report.latex.tex_cross_validation
        Function to report cross validation metrics.

    Returns
    -------
    tex : str
        Report of the pipeline in tex format.
    """
    mustache = {'estimators': []}
    mustache['datasets'] = dataset_tex_fun(pipeline.statistics_results)
    mustache['performance_overview'] = tex_performance_overview(pipeline.performance_results)
    mustache['fairness_overview'] = tex_fairness_overview(pipeline.fairness_results)

    for estimator, results in pipeline.performance_results.items():
        est_name = estimator_name(estimator)
        est_dict = {'estimator_name': est_name}

        mtbl = performance_tex_fun(est_name, results)
        est_dict['metrics_table'] = mtbl

        if estimator in pipeline.fairness_results:
            fair = fairness_tex_fun(
                est_name, pipeline.fairness_results[estimator])
            est_dict['fairness_evaluation'] = fair

        if pipeline.cross_validation:
            cv = cross_validation_tex_fun(est_name,
                                          pipeline.cross_validation[estimator])
            est_dict["cross_validation"] = cv

        # add_models = results.get("additional_models", [])
        # est_dict["additional_model_info"] = \
        #     tex_additional_models(estimator, add_models,
        #                           feature_names, class_names)

        mustache['estimators'].append(est_dict)

    tex = rc.get_text("reports/latex/report.tex")
    tex = chevron.render(tex, mustache)
    return tex
