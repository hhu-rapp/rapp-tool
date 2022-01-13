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
    is_efficient = np.ones(costs.shape[0], dtype = bool)
    for i, c in enumerate(costs):
        is_efficient[i] = np.all(np.any(costs[:i]<=c, axis=1)) and np.all(np.any(costs[i+1:]<c, axis=1))
    return is_efficient
