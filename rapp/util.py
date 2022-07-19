import numpy as np


def pareto_front(costs):
    """
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
    # Above line marls only the first duplicate of an element in Pareto front.
    # Code below marks other duplicates in pareto front as well.
    for i, c in enumerate(costs):
        if is_efficient[i]:
            duplicate_idx = np.argwhere(np.all(costs == c, axis=1)).flatten()
            print(c, is_efficient[duplicate_idx])
            is_efficient[duplicate_idx] = is_efficient[i]
    return is_efficient


def estimator_name(estimator):
    """
    Return
    ------
    Simple class name of the estimator.
    """
    return estimator.__class__.__name__


def max_difference(values):
    """
    Parameters
    ----------
    values: (n_samples,)

    Return
    ------
    Maximal pairwise difference.
    """
    max_difference = -1

    n = len(values)
    for i in range(n):
        for j in range(i+1, n):
            diff = abs(values[i] - values[j])

            if diff > max_difference:
                max_difference = diff

    return max_difference
