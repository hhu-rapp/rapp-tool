"""
Contains the dispatching logic for translating additional model information
into TeX files.
"""

# Note: The dispatcher is at the bottom of the file.
# If you need to introduce another call, add it there.

import chevron

import rapp.report.resources as rc
from rapp.report.latex.tables import tex_performance, tex_fairness


def _default_dispatch(additional_model_info):
    return ""


def tex_additional_models(model_name, additional_model_data: list):
    global dispatcher

    if len(additional_model_data) == 0:
        return ""

    return dispatcher.get(model_name, _default_dispatch)(additional_model_data)


def tex_ccp(model_data):
    """
    Translates the additional model data from cost-complexity pruning
    of a DecisionTreeClassifier into LaTeX code.

    Parameters
    ----------
    model_data : list(dict)
        List of dictionaries satisfying the following specification:

            {"alpha": float,
             "depth": int,
             "pareto_front": bool,
             "train": dict,
             "test": dict}

        The modes train and test will be translated by
        `rapp.report.latex.tex_performance`.
    """
    # We will do three things
    #   1. Plot the depth vs. the balanced accuracy, marking the pareto front
    #   2. Report the performances and fairnesses of each tree
    #   3. Visualise each tree

    mustache = {"pareto_coords": [],
                "nonpareto_coords": []}

    # Gather the data points for the plot
    for data in model_data:
        depth = data["depth"]
        alpha = data["alpha"]
        is_pareto = data["pareto_front"]
        bacc = data["test"]["scores"]["Balanced Accuracy"]
        point = {"depth": depth, "performance": bacc, "alpha": alpha}
        if is_pareto:
            mustache["pareto_coords"] += [point]
        else:
            mustache["nonpareto_coords"] += [point]

    # Report data for each individual tree from the pareto front
    pareto_front = [p for p in model_data if p["pareto_front"]]
    pareto_front = sorted(pareto_front,
                          key=lambda p: p["alpha"])

    pareto_mustache = []
    for pareto in pareto_front:
        estimator = rf"DecisionTreeClassifier (\(\alpha={pareto['alpha']}\))"
        performance = tex_performance(estimator, pareto)
        fairness = tex_fairness(estimator, pareto)

        pareto_mustache.append({
            "title": estimator,
            "performance_table": performance,
            "fairness_table": fairness
        })

    mustache["pareto_front"] = pareto_mustache

    tex_template = rc.get_text("cost_complexity_pruning.tex")
    return chevron.render(tex_template, mustache)


# This is a naive dispatcher implementation based on a dictionary.
# Simply commit the key and the dispatching method into the dict.
# Default implementation is _default_dispatch
dispatcher = {
    "DecisionTreeClassifier": tex_ccp,
}
