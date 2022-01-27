import logging as log

from functools import singledispatch
from sklearn.tree import DecisionTreeClassifier

from rapp.pipeline.training.dt import cost_complexity_pruning

@singledispatch
def get_additional_models(estimator, X, y):
    """
    Creates additional models based on the input estimator's type.
    Returns a (potentially empty) list of additionally trained models.
    Hereby, the models are wrapped in a dictionary with the `model` key
    pointing to the trained model.
    An `id` key may be set externally from the pipeline.
    A key `safe_model` may be set to True or False to indicate whether the
    model should be saved. If the key is not present, the logic defaults to
    True.
    Further keys are dependent on the
    base model type.
    """
    return []


@get_additional_models.register
def _(estimator: DecisionTreeClassifier, X, y):
    log.info("Training additional models for DecisionTreeClassifier")
    return cost_complexity_pruning(estimator, X, y)
