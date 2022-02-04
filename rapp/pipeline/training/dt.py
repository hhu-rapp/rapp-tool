import logging as log
import numpy as np

from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import balanced_accuracy_score
from sklearn.metrics import make_scorer
from sklearn.model_selection import cross_val_score

from rapp.util import pareto_front


def cost_complexity_pruning(estimator, X, y, scoring=balanced_accuracy_score):
    """
    Conducts a cost complexity pruning over a decision tree classifier
    and returns a list of results.

    Parameters
    ----------
    estimator : DecisionTreeClassifier
        An already fitted decision tree.
    X :
        Data.
    y :
        Labels.
    scoring :
        A scoring method for the pareto front.
        Default to sklearn.metrics.balanced_accuracy_score.

    Returns
    -------
    list(dict)
        Each element of the list is a dictionary of the form

            {'model': DecisionTreeClassifier,
             'alpha': int,
             'depth': int,
             'pareto_front': bool}

        with the keys corresponding to the trained model,
        the used ccp alpha value, the resulting tree depth,
        and whether the model resides in the pareto front for the
        tree-depth vs. scoring method.
    """


    ccp_path = estimator.cost_complexity_pruning_path(X, y)
    alphas = ccp_path["ccp_alphas"][:-1]

    models = []
    for alpha in alphas:
        if alpha < 0:
            log.debug("Skipping CCP for negative alpha: %s", alpha)
            continue  # Skip edgecase when alpha is negative.
        # Use hyperparameters of OG model
        params = estimator.get_params()
        params["ccp_alpha"] = alpha
        clf = DecisionTreeClassifier(**params)
        log.debug("Fit cost complexity pruning with alpha=%s", alpha)
        clf.fit(X, y)
        clf_info = {
            'model': clf,
            'alpha': alpha,
            'depth': clf.tree_.max_depth,
            'save_model': False,
            'pareto_front': False  # Will be correctly set below.
        }
        log.debug("Finish: Fit cost complexity pruning with alpha=%s", alpha)
        models.append(clf_info)

    # convert scoring metric to scorer
    scorer = make_scorer(scoring)

    # collect depths and performance for pareto optima
    costs = []
    for clf_info in models:
        depth = clf_info["depth"]
        est = clf_info["model"]
        score = np.mean(cross_val_score(est, X, y, scoring=scorer, cv=5))

        # We use the negative depth so that we actually minimise the depth.
        costs.append([-depth, score])
    costs = np.array(costs)

    indices, = np.nonzero(pareto_front(costs))

    # Update values as promised.
    for i in indices:
        models[i]['pareto_front'] = True
        models[i]['save_model'] = True

    return models
