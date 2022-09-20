import numpy as np


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
            diff = np.abs(values[i] - values[j])

            if diff > max_difference:
                max_difference = diff

    return max_difference
