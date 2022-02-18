import logging

from sklearn.metrics import accuracy_score
from sklearn.metrics import balanced_accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import make_scorer
from sklearn.model_selection import cross_validate
from sklearn.model_selection import train_test_split
import pandas as pd

from rapp import sqlbuilder
from rapp import models
from rapp import data as db

log = logging.getLogger('rapp.pipeline')


class Pipeline():
    """
    Attributes
    ----------
    estimators : list
        List of Scikit-learn estimators.

    data : dict
        Has the form
        ```
        {"train": {"X": Dataframe, "y": Dataframe, "z": Dataframe},
         "test": {"X": Dataframe, "y": Dataframe, "z": Dataframe}}
        ```

    database_file : str
        Path/Name of the used database file.

    sql_query : str
        Used SQL-Query to access the data from the database_file

    type : {'classification', 'regression}
        Which type of prediction task is tackled by the pipeline.

    score_functions : dict[name -> function]
        Dictionary of the score functions used for performance evaluation.
        Keys are the natural language names of the scoring functions
        while the values are callables expecting ground truth and prediction
        labels as input.

    cross_validation : dict[estimator -> results]
        Dictionary containing per estimator in pipeline.estimators
        the cross validation results over the training set.
    """

    def __init__(self, config):
        """
        Parameters
        ----------
        config :
            Data object containing the desired pipeline configuration.
        seed : int, default = 1337
            Random Seed on startup from pipeline
        """
        self.config = config  # Keep for reference.
        self.type = config.type
        self.estimators = _parse_estimators(config.estimators, self.type)

        self.database_file = config.filename
        self.sql_query = _load_sql_query(config)

        self.data = self.prepare_data()

        self.score_functions = _get_score_functions(self.type)

    def prepare_data(self):
        log.debug('Connecting to db %s', self.database_file)
        con = db.connect(self.database_file)

        log.debug('Loading SQL query', self.database_file)
        df = db.query_sql(self.sql_query, con)

        return _load_test_split_from_dataframe(df, self.config)

    def get_data(self, mode):
        """
        Parameters
        ----------
        mode : {'train', 'test'}

        Returns
        -------
        X, y, z : Dataframe
            Dataframes containing the data related to the specified mode.
        """
        X = self.data[mode]['X']
        y = self.data[mode]['y']
        z = self.data[mode]['z']
        return X, y, z


def _parse_estimators(estimator_ids, mode):
    """
    Parameters
    ----------
    estimators_ids: list(str)
        List of string ids to translate into a respective instance of their
        class. Entries are expected to match keys in `rapp.models.models`.
    mode: {'classification', 'regression'}

    Returns
    -------
    estimators:
        A list of instantiated ML models that can be trained via `fit` method.
    """
    getter = (models.get_regressor
              if mode == 'regression' else models.get_classifier)

    return [getter(est_id) for est_id in estimator_ids]


def _load_sql_query(config):
    sql = None
    if hasattr(config, 'sql_file') and config.sql_file is not None:
        with open(config.sql_file, 'r') as f:
            sql = f.read()
    elif hasattr(config, 'sql_query') and config.sql_query is not None:
        sql = config.sql_query
    else:
        feature_id = f"{config.studies_id}_{config.features_id}"
        label_id = config.labels_id
        sql = sqlbuilder.load_sql(feature_id, label_id)

    return sql


def _load_test_split_from_dataframe(df, config, random_state=42):
    # Convention: If no label name given, we use the last column.
    label_col = (config.label_name
                 if hasattr(config, 'label_name') and config.label_name
                 else df.columns[-1])

    # create data
    X = df.drop(label_col, axis=1, inplace=False)
    y = df[[label_col]]
    # TODO: What if sensitive_attributes is empty?
    z = X[config.sensitive_attributes]

    # Adapt to categorical data.
    cat_columns = [c for c in config.categorical if c != label_col]
    if cat_columns != []:
        categorical = pd.get_dummies(data=X[cat_columns], columns=cat_columns)
        X = pd.concat([X, categorical], axis=1)
        # Remove old categorical attributes from input features
        X = X.drop(cat_columns, axis=1)

    # split datasets
    # TODO: What about the random seed? Keep fixed or make RNG part of config?
    split = train_test_split(X, y, z, train_size=0.8,
                             random_state=random_state)
    X_train, X_test, y_train, y_test, z_train, z_test = split

    data = {"train": {"X": X_train, "y": y_train, "z": z_train},
            "test": {"X": X_test, "y": y_test, "z": z_test}}

    return data


def train_models(pipeline, cross_validation=False):
    """
    Trains the models which are stored in the `pipeline`.

    Parameters
    ----------
    pipeline : Pipeline instance

    cross_validation : bool, default = False
        Whether or not the models should be trained with cross validation
        as well.
        Cross validation results are stored separately in the pipeline,
        while the main models are always trained on the whole data corpus.

    cv_scores : iterable
        List of scorer functions passed to the cross validation step.
        Only relevant if `cross_validation` is True.

    Returns
    -------
    pipeline
        Reference to the pipeline which was put in.
    """
    X_train, y_train, _ = pipeline.get_data('train')
    for est in pipeline.estimators:
        log.info("Training model: %s", est)
        est.fit(X_train, y_train)
        if cross_validation:
            k = 5  # Number of fold, hard coded for now.
            log.info("%s-fold crossvalidation on model: %s", k, est)

            # Translate our functions into scorers
            scorers = {name: make_scorer(fun)
                       for name, fun in pipeline.score_functions.items()}

            cv_result = cross_validate(est, X_train, y_train, cv=k,
                                       scoring=scorers,
                                       return_estimator=True,
                                       return_train_score=True)

            pipeline.cross_validation[est] = cv_result

    return pipeline


def _get_score_functions(type: str):
    if type == 'classification':
        scores = {
            'Accuracy': accuracy_score,
            'Balanced Accuracy': balanced_accuracy_score,
            'F1': lambda x, y: f1_score(x, y, average='macro'),
            'Recall': lambda x, y: recall_score(x, y, average='macro'),
            'Precision': lambda x, y: precision_score(x, y, average='macro'),
            'Area under ROC': lambda x, y: roc_auc_score(x, y, multi_class='ovr')
        }
    elif type == 'regression':
        raise NotImplemented('Scoring functions for regression are NYI.')
    else:
        log.error("Unknown ML type '%s'; unable to select scoring functions",
                  type)
        scores = {}

    return scores
