from sklearn.metrics import confusion_matrix

def clf_fairness(clf, fairness, X, y, Z, pred=None, fav_label=1):
    """
    Assesses the fairness of the given classifier over the data (X, y, z).
    For each column c in `z`, a dictionary of the following form is returned

        {c: {
                0: {"favourable_outcome": number_with_fav_outcome,
                    "unfavourable_outcome": number_without_fav_outcome,
                    "confusion_matrix": ... },
                1: {"favourable_outcome": number_with_fav_outcome,
                    "unfavourable_outcome": number_without_fav_outcome,
                    "confusion_matrix": ... },
                # ...
            },
         # ...
         }

    where one key for each unique value of the respective column exists.

    Parameters
    ----------
    clf: Classifier with a `.predict(X)` method.
    fairness: Fairness function from `rapp.fair.notions`.
    X: Feature values of the input data, assumed as Pandas data frame.
    y: Ground-truth labels of the input data.
    Z: Dataframe of sensitive attributes for input data.
    pred: (default=None)
        Predictions from classifier for X. If `pred=None`, `clf.predict(X)` will be called.
    fav_label: (default=1)
        Value of the favourable outcome of the prediction.

    Returns
    -------
    dict: See description.
    """
    if pred is None:
        pred = clf.predict(X)

    fair_results = {}
    for c in Z.columns:
        fair_results[c] = {}
        fair_results[c]['outcomes'] = fairness(X, y, Z[c], pred, fav_label)


    return fair_results


def __get_confusion_matrix(y_true, y_pred):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    return {
        'tp': tp,
        'fp': fp,
        'tn': tn,
        'fn': fn,
    }


def group_fairness(X, y, z, pred, fav_label=1):
    fair = {}

    values = z.unique()
    for v in values:
        mask = (z == v)
        pred_v = pred[mask]

        fav = pred_v[pred_v == fav_label]

        fair[v] = {
            "affected_total": len(fav),
            "affected_percent": len(fav)/len(pred_v),
            "confusion_matrix": __get_confusion_matrix(y[mask], pred[mask])
        }

    return fair


def predictive_equality(X, y, z, pred, fav_label=1):
    fair = {}

    values = z.unique()
    for v in values:
        mask = (z == v)
        pred_v = pred[mask & (y != fav_label)]

        fav = pred_v[pred_v == fav_label]

        fair[v] = {
            "affected_total": len(fav),
            "affected_percent": len(fav)/len(pred_v),
            "confusion_matrix": __get_confusion_matrix(y[mask], pred[mask])
        }

    return fair


def equality_of_opportunity(X, y, z, pred, fav_label=1):
    fair = {}

    values = z.unique()
    for v in values:
        mask = (z == v)
        pred_v = pred[mask & (y == fav_label)]

        fav = pred_v[pred_v == fav_label]

        fair[v] = {
            "affected_total": len(fav),
            "affected_percent": len(fav)/len(pred_v),
            "confusion_matrix": __get_confusion_matrix(y[mask], pred[mask])
        }

    return fair
