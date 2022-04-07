import chevron
import rapp.report.resources as rc

from rapp.util import estimator_name
from rapp.pipeline import Pipeline

from rapp.report.latex.tables import tex_fairness, tex_performance_table, tex_cross_validation
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
        for group in dataset["groups"].keys():
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
        for label in dataset["outcomes"].keys():
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

    template = rc.get_text("dataset_table.tex")
    tex = chevron.render(template, mustache)
    return tex


def tex_dataset_plot(report):

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
        for group in dataset["groups"].keys():
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
        for label in dataset["outcomes"].keys():
            unique_labels = []
            for i in range(dataset["outcomes"][label]):
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
                        label_group_data["label_subgroups"].append(
                            label_sub_data)
                    label_data["label_groups"].append(label_group_data)
                labels.append(label_data)

        mode_data = {"mode": mode.capitalize(),
                     "total": dataset["total"],
                     "groups": groups,
                     "labels": labels}
        mustache["modes"].append(mode_data)

    template = rc.get_text("dataset_plots.tex")
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
        fairness_tex_fun=tex_fairness,
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

    tex = rc.get_text("report.tex")
    tex = chevron.render(tex, mustache)
    return tex
