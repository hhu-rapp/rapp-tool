"""
Organisation of usecases and methods for different ML models.
The necessary functions are determined by the respective getters.
"""

# ML classifiers
from numpy import mod
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier

# ML regression methods
from sklearn.linear_model import ElasticNet
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import BayesianRidge
from sklearn.tree import DecisionTreeRegressor
from sklearn.kernel_ridge import KernelRidge
from sklearn.neural_network import MLPRegressor

# Dispatch information about how models are called and which methods are used.
models = {
    'classification': {
        'RF': {'class': RandomForestClassifier,
               'kwargs': {'random_state': 0}
               },
        'DT': {'class': DecisionTreeClassifier,
               'kwargs': {'random_state': 0,
                          'class_weight': 'balanced'}
               },
        'SVM': {'class': SVC,
                'kwargs': {'random_state': 0}
                },
        'NB': {'class': GaussianNB,
               'kwargs': {}
               },
        'LR': {'class': LogisticRegression,
               'kwargs': {'random_state': 0}
               },
        'NN': {'class': MLPClassifier,
               'kwargs': {'random_state': 0}
               },
    },
    'regression': {
        'EL': {'class': ElasticNet,
               'kwargs': {'random_state': 0}
               },
        'LR': {'class': LinearRegression,
               'kwargs': {}
               },
        'BR': {'class': BayesianRidge,
               'kwargs': {}
               },
        'DT': {'class': DecisionTreeRegressor,
               'kwargs': {'random_state': 0}
               },
        'KR': {'class': KernelRidge,
               'kwargs': {}
               },
        'NN': {'class': MLPRegressor,
               'kwargs': {'random_state': 0}
               },
    }
}


def get(model_id, **model_args):
    """
    Returns a classification model object for a given `model_id`.
    """
    return get_classifier(model_id, **model_args)


def get_classifier(model_id, **model_args):
    """
    Returns a classification model object for a given `model_id`.
    """
    global models
    model_info = models['classification'][model_id]
    constructor = model_info['class']
    # Allow user-specified args.
    kwargs = {**model_info['kwargs'], **model_args}
    mod = constructor(**kwargs)

    return mod


def get_regressor(model_id, **model_args):
    """
    Returns a regression model object for a given `model_id`.
    """
    global models
    model_info = models['regression'][model_id]
    constructor = model_info['class']
    # Allow user-specified args.
    kwargs = {**model_info['kwargs'], **model_args}
    mod = constructor(**kwargs)

    return mod
