from cmath import exp
import numpy as np

from rapp.util import pareto_front

def test_pareto_extrema_only():
    data = np.array([(1,5), (1, 1), (5,1)])

    expected = [True, False, True]
    actual = pareto_front(data).tolist()

    assert expected == actual


def test_pareto_with_elements_inbetween():
    data = np.array([(1,5), (2, 2), (5,1)])

    expected = [True, True, True]
    actual = pareto_front(data).tolist()

    assert expected == actual


def test_pareto_bigger_example():
    data = np.array([(1,5), (3,5), (4,4), (2,1), (5,4)])

    expected = [False, True, False, False, True]
    actual = pareto_front(data).tolist()

    assert expected == actual


def test_pareto_bigger_one_pareto_optimum():
    data = np.array([(1,5), (3,5), (4,4), (2,1), (5,4), (9,9)])

    expected = [False, False, False, False, False, True]
    actual = pareto_front(data).tolist()

    assert expected == actual


def test_pareto_with_negative_values():
    axis1 = [ 4,  5,  6,  2,  5]
    axis2 = [-2, -3, -2, -6, -1]
    data = np.array(list(zip(axis1, axis2)))

    expected = [False, False, True, False, True]
    actual = pareto_front(data).tolist()

    assert expected == actual


def test_pareto_example_to_minimise_second_dimension():
    axis1 = [ 4,  5,  6,  2,  5]
    axis2 = [ 2,  3,  2,  6,  1]
    axis2neg = [-x for x in axis2]
    data = np.array(list(zip(axis1, axis2)))

    data2 = data.copy()
    data2[:,1] = -data[:,1]

    expected = [[6,2],[5,1]]
    pareto = pareto_front(data2)
    actual = data[pareto].tolist()

    assert expected == actual


def test_pareto_with_double_entries_not_in_pareto_front():
    data = np.array([(1,5), (3,5), (4,4), (1,5), (2,1), (5,4)])

    expected = [False, True, False, False, False, True]
    actual = pareto_front(data).tolist()

    assert expected == actual


def test_pareto_with_double_entries_in_pareto_front():
    data = np.array([(1,5), (4,4), (5,4), (5,4)])

    expected = [True, False, True, True]
    actual = pareto_front(data).tolist()

    assert expected == actual


def test_pareto_with_multiple_duplicates():
    data = np.array([(1,5), (2,2), (5,4), (2,2), (5,4)])

    expected = [True, False, True, False, True]
    actual = pareto_front(data).tolist()

    assert expected == actual
