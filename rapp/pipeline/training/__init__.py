from functools import singledispatch
from sklearn.tree import DecisionTreeClassifier

from rapp.pipeline.training.dt import cost_complexity_pruning

@singledispatch
def get_additional_models(estimator, X_train, y_train, X_val, y_val):
    """
    Creates additional models based on the input estimator's type.
    Returns a (potentially empty) list of additionally trained models.
    Hereby, the models are wrapped in a dictionary with the `model` key
    pointing to the trained model. Further keys are dependent on the
    base model type.
    """
    return []


@get_additional_models.register
def _(estimator: DecisionTreeClassifier, X_train, y_train, X_val, y_val):

    return cost_complexity_pruning(estimator, X_train, y_train, X_val, y_val)
