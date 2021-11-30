import numpy as np

def pareto_front(costs):
    """
    Parameters
    ----------
    costs: array-like (n_samples, n_costs)
        Costs from which to extract the pareto optimal indices.

    Returns
    -------
    array (n_samples,)
        Indices of pareto-optimal samples.
    """
    # Adapted from https://stackoverflow.com/a/40239615
    is_efficient = np.ones(costs.shape[0], dtype = bool)
    for i, c in enumerate(costs):
        is_efficient[i] = np.all(np.any(costs[:i]<=c, axis=1)) and np.all(np.any(costs[i+1:]<c, axis=1))
    idxs, = np.nonzero(is_efficient)
    return idxs
