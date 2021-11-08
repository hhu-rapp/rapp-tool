import chevron
import rapp.report.resources as rc


def tex_classification_report(report):
    mustache = {'estimators': []}
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
