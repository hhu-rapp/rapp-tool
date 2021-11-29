import chevron
import rapp.report.resources as rc


def tex_dataset_report(report):

    # Tex file expects the following format for Chevron per mode
    # {'total': int,
    #  'groups: list({'group_name': str,
    #                 'group_size': int,
    #                 'start_column': int,
    #                 'end_column': int,
    #                 'group_total': int,
    #                 'subgroups': list({'sub_name': str, 'sub_count': int})}),
    #  'labels': list({'label': any,
    #                  'label_total': int,
    #                  'label_groups': list({
    #                    'label_group_total': int,
    #                    'label_subgroups': list({
    #                      'label_sub_name': string,
    #                      'label_sub_count})})})}

    mustache = {'modes': []}
    for mode in ["train", "test"]:
        dataset = report[mode]

        # Fill in the group names
        groups = []
        start_col_counter = 2
        for group in dataset["groups"].keys():
            group_data = {'group_name': group,
                          'group_total': dataset["total"],
                          'subgroups': []}
            for sub in dataset["groups"][group].keys():
                sub_data = {
                    "sub_name": sub,
                    "sub_count": dataset["groups"][group][sub]["total"]
                }
                group_data["subgroups"].append(sub_data)
            group_data["size"] = len(group_data["subgroups"])+1 # +1 for all-column
            group_data["start_column"] = start_col_counter
            group_data["end_column"] = start_col_counter + group_data["size"] -1
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


def tex_classification_report(report):
    mustache = {'estimators': [],
                'datasets': tex_dataset_report(report)}

    for estimator, results in report["estimators"].items():
        est_dict = {'estimator_name': estimator}
        # Metrics table
        mtbl = rc.get_text("metrics_table.tex")
        metrics = []
        for m in results["train"]["scores"].keys():
            res = {'name': m,
                   'train': f"{results['train']['scores'][m]:.3f}",
                   'test': f"{results['test']['scores'][m]:.3f}",
                   }
            metrics.append(res)
        mtbl = chevron.render(mtbl, {'metrics': metrics,
                                     'title': estimator})

        fair = tex_fairness(estimator, results)
        est_dict['fairness_evaluation'] = fair

        est_dict['metrics_table'] = mtbl
        mustache['estimators'].append(est_dict)

    tex = rc.get_text("report.tex")
    tex = chevron.render(tex, mustache)
    return tex


def tex_fairness(estimator, data):
    fairness = {'title': estimator,
                'groups': []}

    # Building a dictionary of the following form
    # {'title': estimator_name,
    #  'groups': [
    #      # for each group
    #      {'group': group_label,
    #       'train': {'notions': [
    #           # for each notion
    #           {'notion': notion_name,
    #            'measures': [{'value': value}, ...],
    #            'difference': difference_if_binary},
    #           ...]},
    #       'test': {'notions': [
    #           # for each notion
    #           {'notion': notion_name,
    #            'measures': [{'value': value}, ...],
    #            'difference': difference_if_binary},
    #           ...]}}]}
    for group in data["train"]["fairness"].keys():
        group_dict = {'group': group,
                      'train': {'notions': []},
                      'test': {'notions': []},
                      'outs': [],
                      }
        for notion in data["train"]["fairness"][group].keys():
            for set in ["train", "test"]:
                fair_data = data[set]["fairness"]

                out_data = fair_data[group][notion]['outcomes']

                outs = list(out_data.keys())
                # Add outputs exactly once.
                if len(group_dict["outs"]) == 0:
                    for o in outs:
                        group_dict["outs"].append({'output_name': o})
                    group_dict["last_out_col"] = len(outs)+1

                if len(outs) == 2:
                    group_dict["has_diff"] = True
                    diff = abs(out_data[outs[0]]["affected_percent"]
                               - out_data[outs[1]]["affected_percent"])
                else:
                    diff = "-"

                measures = []
                for o in outs:
                    measures.append({'value':
                                     f"{out_data[o]['affected_percent']:.3f}"})

                notion_dict = {
                    'notion': notion,
                    'measures': measures,
                    'difference': f"{diff:.3f}"
                }
                group_dict[set]['notions'].append(notion_dict)
        fairness['groups'].append(group_dict)

    tex = rc.get_text("fairness_table.tex")
    tex = chevron.render(tex, fairness)
    return tex
