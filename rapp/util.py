import numpy as np


def pareto_front(costs):
    """
    Calculate the Pareto front from costs.
    Treated as maximization problem:
    A point pareto dominates another point if all costs of it are greater.

    Parameters
    ----------
    costs: np.array (n_samples, n_costs)
        Costs from which to extract the pareto optimal indices.

    Returns
    -------
    np.array (n_samples,)
        Boolean array indicating whether the respective index' element
        is part of the Pareto front or not.
    """
    # Adapted from https://stackoverflow.com/a/40239615
    is_efficient = np.ones(costs.shape[0], dtype=bool)
    for i, c in enumerate(costs):
        if is_efficient[i]:
            # Keep any point with a lower cost.
            is_efficient[is_efficient] = np.any(costs[is_efficient] > c,
                                                axis=1)
            is_efficient[i] = True  # And keep self.
    # Above line marks only the first duplicate of an element in Pareto front.
    # Code below marks other duplicates in pareto front as well.
    for i, c in enumerate(costs):
        if is_efficient[i]:
            duplicate_idx = np.argwhere(np.all(costs == c, axis=1)).flatten()
            is_efficient[duplicate_idx] = is_efficient[i]
    return is_efficient


def estimator_name(estimator):
    """
    Return
    ------
    Simple class name of the estimator.
    """
    return estimator.__class__.__name__
