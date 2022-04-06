import chevron
import rapp.report.resources as rc

from rapp.util import estimator_name
from rapp.pipeline import Pipeline

from rapp.report.latex.tables import tex_fairness, tex_performance_table, tex_cross_validation
from rapp.report.latex.additionalmodels import tex_additional_models


def tex_dataset_report(report):

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


def tex_report(report, stats_plot=False):
    mustache = {'estimators': []}

    if stats_plot:
        mustache['datasets'] = tex_dataset_plot(report["statistics"])
    if not stats_plot:
        mustache['datasets'] = tex_dataset_report(report["statistics"])

    for estimator, results in report["performance"].items():
        est_name = estimator_name(estimator)
        est_dict = {'estimator_name': est_name}

        mtbl = tex_performance_table(est_name, results)
        est_dict['metrics_table'] = mtbl

        if estimator in report["fairness"]:
            fair = tex_fairness(est_name, report["fairness"][estimator])
            est_dict['fairness_evaluation'] = fair

        if report["cross_validation"]:
            est_dict["cross_validation"] = tex_cross_validation(est_name,
                                                                report["cross_validation"][estimator])

        # add_models = results.get("additional_models", [])
        # est_dict["additional_model_info"] = \
        #     tex_additional_models(estimator, add_models,
        #                           feature_names, class_names)

        mustache['estimators'].append(est_dict)

    tex = rc.get_text("report.tex")
    tex = chevron.render(tex, mustache)
    return tex


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
    mustache = {'estimators': []}
    mustache['datasets'] = tex_dataset_report(pipeline.statistics_results)

    for estimator, results in pipeline.performance_results.items():
        est_name = estimator_name(estimator)
        est_dict = {'estimator_name': est_name}

        mtbl = tex_performance_table(est_name, results)
        est_dict['metrics_table'] = mtbl

        if estimator in pipeline.fairness_results:
            fair = tex_fairness(est_name, pipeline.fairness_results[estimator])
            est_dict['fairness_evaluation'] = fair

        if estimator in pipeline.cross_validation:
            est_cv = tex_cross_validation(est_name,
                                          pipeline.cross_validation[estimator])
            est_dict["cross_validation"] = est_cv

        # add_models = results.get("additional_models", [])
        # est_dict["additional_model_info"] = \
        #     tex_additional_models(estimator, add_models,
        #                           feature_names, class_names)

        mustache['estimators'].append(est_dict)

    tex = rc.get_text("report.tex")
    tex = chevron.render(tex, mustache)
    return tex
