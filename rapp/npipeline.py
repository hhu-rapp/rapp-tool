import logging

# classification metrics
from sklearn.metrics import accuracy_score
from sklearn.metrics import balanced_accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import make_scorer
from sklearn.metrics import confusion_matrix
# regression metrics
from sklearn.metrics import max_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
# evaluation
from sklearn.model_selection import cross_validate
from sklearn.model_selection import train_test_split
import pandas as pd

from rapp import sqlbuilder
from rapp import models
from rapp import data as db
from rapp.fair import notions
from rapp.util import estimator_name

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

    cross_validation : dict[estimator -> results]
        Dictionary containing per estimator in pipeline.estimators
        the cross validation results over the training set.

    score_functions : dict[name -> function]
        Dictionary of the score functions used for performance evaluation.
        Keys are the natural language names of the scoring functions
        while the values are callables expecting ground truth and prediction
        labels as input.

    fairness_functions : dict[name -> function]
        Dictionary of the norms used for fairness evaluation.
        Keys are the natural language names of the norms
        while the values are callables of the form

            fun(X, y, z, pred, fav_label=1)

        expecting the test data's features X, labels y, protected attributes z,
        and a classifier's predictions pred as input.
        Optionally, the favourable label can be set via fav_label, assuming
        the default 1.

    protected_attributes : list[str]
        List of protected attribute names. May be empty.

    performance_results : dict[estimator -> results]
        Dictionary with estimators as key which map onto possibly
        calculated performance results.

        A performance result has the form

            {mode:
                {'scores': {score_functions_results},
                'confusion_matrix' : confusion_matrix_results}}

    statistics_results : dict[mode -> statistics]
        Dictionary with mode as key which map onto calculated statistics.

    fairness_results : dict[estimator -> results]
        Dictionary with estimators as key which map onto possibly
        calculated fairness results.

        A fairness result has the form

            {protected_attribute:
                {notion_name: {'train': train_results,
                               'test': test_results}},
                 ...}

        where the dictionary over group IDs is described by
        `rapp.fair.notions.clf_fairness()`.
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

        if config.filename is not None:
            self.database_file = config.filename
            self.sql_query = _load_sql_query(config)
            self.data = self.prepare_data()
        else:
            self.data = self.prepare_data_from_df(config.sql_df)

        self.sensitive_attributes = config.sensitive_attributes

        self.score_functions = _get_score_functions(self.type)

        self.cross_validation = {}
        self.fairness_results = {}
        self.performance_results = {}
        self.statistics_results = {}

        # Fixme: The below fairness notions do not make sense for regression.
        self.fairness_functions = {
            'Statistical Parity': notions.group_fairness,
            'Predictive Equality': notions.predictive_equality,
            'Equality of Opportunity': notions.equality_of_opportunity,
        }

    def prepare_data(self):
        log.debug('Connecting to db %s', self.database_file)
        con = db.connect(self.database_file)

        log.debug('Loading SQL query', self.database_file)
        df = db.query_sql(self.sql_query, con)

        return _load_test_split_from_dataframe(df, self.config)

    def prepare_data_from_df(self, df):
            return _load_test_split_from_dataframe(df, self.config)

    def get_data(self, mode):
        """
        Parameters
        ----------
        mode : {'train', 'test'}

        Returns
        -------
        X, z : Dataframe
            Dataframes containing the data related to the specified mode.
        y
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
        est.fit(X_train, y_train.to_numpy().ravel())
        if cross_validation:
            k = 5  # Number of fold, hard coded for now.
            log.info("%s-fold crossvalidation on model: %s", k, est)

            # Translate our functions into scorers
            scorers = {name: make_scorer(fun)
                       for name, fun in pipeline.score_functions.items()}

            cv_result = cross_validate(est, X_train, y_train.to_numpy().ravel(), cv=k,
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
            'F1': lambda y, y_pred: f1_score(y, y_pred, average='macro'),
            'Recall': lambda y, y_pred: recall_score(y, y_pred, average='macro'),
            'Precision': lambda y, y_pred: precision_score(y, y_pred, average='macro'),
            'Area under ROC': lambda y, y_pred: roc_auc_score(y, y_pred, multi_class='ovr')
        }
    elif type == 'regression':
        scores = {
            'Mean Absolute Error': mean_absolute_error,
            'Mean Squared Error': mean_squared_error,
            'Max Error': max_error,
            'R2': r2_score,
        }
    else:
        log.error("Unknown ML type '%s'; unable to select scoring functions",
                  type)
        scores = {}

    return scores


def evaluate_fairness(pipeline):
    for est in pipeline.estimators:
        res = evaluate_estimator_fairness(est,
                                          pipeline.data,
                                          pipeline.fairness_functions,
                                          pipeline.sensitive_attributes)

        pipeline.fairness_results[est] = res
    return pipeline


def evaluate_estimator_fairness(estimator, data, notion_dict,
                                protected_attributes=None):
    """
    Parameters
    ----------
    estimator : Trained classifier with predict method

    data : dict
        Structure is assumed to be a mapping from modes to a dict of datasets

            mode_name: {'X': X_df, 'y': y_df, 'z': z_df}

        where usually `mode_name` in {'train', 'test'}.

    notion_dict : dict[str -> callable]
        Dictionary of the norms used for fairness evaluation.
        Keys are the natural language names of the norms
        while the values are callables of the form

            fun(X, y, z, pred, fav_label=1)

        expecting the test data's features X, labels y, protected attributes z,
        and a classifier's predictions pred as input.
        Optionally, the favourable label can be set via fav_label, assuming
        the default 1.

    protected_attributes : list[str], default: None
        Column names of the protected attributes to evaluate.
        If None, all are taken into account.

    Returns
    -------
    fairness_results
        Nested dictionary matching the format for Pipeline.fairness_results.
    """

    est_name = estimator_name(estimator)
    log.info("Evaluating fairness for %s", est_name)

    if protected_attributes is None:
        # Get the protected attributes of one of the data modes.
        # It does not matter which one we get; per convention
        # all need to have the same protected attributes.
        some_set = next(iter(data.values()))
        protected_attributes = some_set['z'].columns
    elif isinstance(protected_attributes, str):
        protected_attributes = [protected_attributes]
    fairness_results = {}

    predictions = {mode: estimator.predict(data[mode]['X']) for mode in data}

    for prot_attr in protected_attributes:
        fairness_results[prot_attr] = {}
        for notion_name, notion in notion_dict.items():
            fairness_results[prot_attr][notion_name] = {}
            for mode in data:
                X, y, z = (data[mode]['X'],
                           data[mode]['y'],
                           data[mode]['z'])
                y = y.squeeze()
                log.debug("Evaluating %s over %s set for %s on %s",
                          notion_name, mode, prot_attr, est_name)
                res = notion(X, y, z[prot_attr], predictions[mode])

                fairness_results[prot_attr][notion_name][mode] = res
    return fairness_results


def evaluate_performance(pipeline):

    for est in pipeline.estimators:
        if pipeline.type == 'classification':
            res = evaluate_estimators_performance(est,
                                                  pipeline.data,
                                                  pipeline.score_functions,
                                                  calc_confusion_matrix=True)
            pipeline.performance_results[est] = res
        else:
            res = evaluate_estimators_performance(est,
                                                  pipeline.data,
                                                  pipeline.score_functions,
                                                  calc_confusion_matrix=False)
            pipeline.performance_results[est] = res
    return pipeline


def evaluate_estimators_performance(estimator, data, score_dict, calc_confusion_matrix=False):
    """
    Parameters
    ----------
    estimator : Trained classifier with predict method

    data : dict
        Structure is assumed to be a mapping from modes to a dict of datasets

            mode_name: {'X': X_df, 'y': y_df, 'z': z_df}

        where usually `mode_name` in {'train', 'test'}.

    score_functions : dict[name -> function]
        Dictionary of the score functions used for performance evaluation.
        Keys are the natural language names of the scoring functions
        while the values are callables expecting ground truth and prediction
        labels as input.

    Returns
    -------
    performance_results
        Nested dictionary matching the format for Pipeline.performance_results.
    """

    est_name = estimator_name(estimator)
    log.info("Evaluating %s", est_name)

    performance_results = {}

    for mode in data:
        performance_results[mode] = {}
        performance_results[mode]["scores"] = {}
        X, y = (data[mode]['X'],
                data[mode]['y'])
        y_pred = estimator.predict(X)

        for score_name, score in score_dict.items():
            log.debug("Evaluating %s over %s set on %s",
                      score_name, mode, est_name)
            res = score(y, y_pred)

            performance_results[mode]["scores"][score_name] = res

        if calc_confusion_matrix:
            cm = confusion_matrix(y, y_pred)
            performance_results[mode]['confusion_matrix'] = cm.tolist()
        else:
            performance_results[mode]['confusion_matrix'] = []

    return performance_results


def calculate_statistics(pipeline):
    for mode in pipeline.data:
        X, y, z = pipeline.get_data(mode)
        res = calculate_set_statistics(X, y, z)
        pipeline.statistics_results[mode] = res
    return pipeline


def calculate_set_statistics(X, y, z):
    """
    Calculates the statistics for a given set.

    Parameters
    ----------
    X : Dataframe
        Features

    y : Dataframe
        Labels

    z : Dataframe
        Protected attributes

    Returns
    -------
    set_stats
        Nested dictionary for the given set matching the format for Pipeline.statistics_results.
    """
    set_stats = {'total': len(y),
                 'outcomes': {},
                 'groups': {}}
    y = y.squeeze()
    values = y.unique()
    for v in values:
        num = len(y[y == v])
        set_stats['outcomes'][v] = num

    for g in z.columns:
        group_stats = {}
        for gvalue in z[g].unique():
            data = y[z[g] == gvalue]
            group_stats[gvalue] = {'total': len(data),
                                   'outcomes': {}}
            for v in values:
                num = len(data[y == v])
                group_stats[gvalue]['outcomes'][v] = num
        set_stats['groups'][g] = group_stats

    return set_stats
