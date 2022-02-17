from rapp import sqlbuilder
from rapp import models
from rapp import data as db
from sklearn.model_selection import train_test_split
import pandas as pd
import logging
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
