

def group_fairness(df, group_names, outcome_name, fav_label=1):
    """
    Assesses the fairness in the dataframe over the given groups.
    Returns a map containing an entry for each specified group in `group_names`.
    For a group G, the entries are:

        result[G] = {
            0: {"favourable_outcome": number_unpriviliged_with_fav_outcome,
                "favourable_outcome": number_unpriviliged_with_fav_outcome},
            1: {"favourable_outcome": number_priviliged_with_fav_outcome,
                "favourable_outcome": number_priviliged_with_fav_outcome},
            "disparity": statistical_disparity_over_priv_and_unpriv_group
        }

    df: A pandas dataframe ccontaining the column `outcome_name` and each of the
        listed `group_names`.
    group_names: A list of column names defining sensitive attributes.
    outcome_name: Name of the column corresponding to the outcome. Assumes 1 as
        favourable outcome and 0 as unfavourable outcome.
    """

    fairnesses = {}
    for group in group_names:
        fair = {}

        priv_mask = df[group] == 1
        priv = df[priv_mask]
        unpriv = df[~priv_mask]

        priv_fav = len(priv[priv[outcome_name] == fav_label])
        priv_unfav = len(priv[priv[outcome_name] != fav_label])
        unpriv_fav = len(unpriv[unpriv[outcome_name] == fav_label])
        unpriv_unfav = len(unpriv[unpriv[outcome_name] != fav_label])

        fair[1] = {"favourable_outcome": priv_fav,
                   "unfavourable_outcome": priv_unfav}
        fair[0] = {"favourable_outcome": unpriv_fav,
                   "unfavourable_outcome": unpriv_unfav}
        fair["disparity"] = priv_fav/len(priv) - unpriv_fav/len(unpriv)

        fairnesses[group] = fair

    return fairnesses


def clf_group_fairness(clf, data, group_names, fav_label=1):
    """
    Assesses the fairness of the give classiier over the dataframe per  group.
    Returns a map containing an entry for each specified group in `group_names`.
    For a group G, the entries are:

        result[G] = {
            0: {"favourable_outcome": number_unpriviliged_with_fav_outcome,
                "favourable_outcome": number_unpriviliged_with_fav_outcome},
            1: {"favourable_outcome": number_priviliged_with_fav_outcome,
                "favourable_outcome": number_priviliged_with_fav_outcome},
            "disparity": statistical_disparity_over_priv_and_unpriv_group
        }

    clf: A classifier with a `predict()` function.
    data: A pandas dataframe containing each of the listed `group_names`.
    group_names: A list of column names defining sensitive attributes.
    """
    test_set = data.copy(deep=True)

    outcol = "Outcome"
    cols = test_set.columns
    while outcol in cols:
        outcol += "_" # We add _ as long as we need to to get a unique name.

    test_set[outcol] = clf.predict(test_set) # Predictions

    return group_fairness(test_set, group_names, outcol, fav_label=fav_label)


def predictive_equality(df, group_names, ground_truth, outcome_name, fav_label=1):
    """
    Assesses the fairness in the dataframe over the given groups.
    Returns a map containing an entry for each specified group in `group_names`.
    For a group G, the entries are:

        result[G] = {
            0: {"favourable_outcome": number_unpriviliged_with_fav_outcome,
                "favourable_outcome": number_unpriviliged_with_fav_outcome},
            1: {"favourable_outcome": number_priviliged_with_fav_outcome,
                "favourable_outcome": number_priviliged_with_fav_outcome},
            "disparity": statistical_disparity_over_priv_and_unpriv_group
        }

    df: A pandas dataframe ccontaining the column `outcome_name` and each of the
        listed `group_names`.
    group_names: A list of column names defining sensitive attributes.
    ground_truth: Name of the column corresponding to the ground truth value.
        Assumes 1 as favourable outcome and 0 as unfavourable outcome.
    outcome_name: Name of the column corresponding to the outcome. Assumes 1 as
        favourable outcome and 0 as unfavourable outcome.
    """

    fairnesses = {}
    for group in group_names:
        fair = {}

        priv = df[(df[group] == 1) & (df[ground_truth]==(1-fav_label))]
        unpriv = df[(df[group] != 1) & (df[ground_truth]==(1-fav_label))]

        priv_fav = len(priv[priv[outcome_name] == fav_label])
        priv_unfav = len(priv[priv[outcome_name] != fav_label])
        unpriv_fav = len(unpriv[unpriv[outcome_name] == fav_label])
        unpriv_unfav = len(unpriv[unpriv[outcome_name] != fav_label])

        fair[1] = {"favourable_outcome": priv_fav,
                   "unfavourable_outcome": priv_unfav}
        fair[0] = {"favourable_outcome": unpriv_fav,
                   "unfavourable_outcome": unpriv_unfav}
        fair["disparity"] = priv_fav/len(priv) - unpriv_fav/len(unpriv)

        fairnesses[group] = fair

    return fairnesses


def clf_predictive_equality(clf, data, ground_truth, group_names, fav_label=1):
    """
    Assesses the fairness of the give classiier over the dataframe per  group.
    Returns a map containing an entry for each specified group in `group_names`.
    For a group G, the entries are:

        result[G] = {
            0: {"favourable_outcome": number_unpriviliged_with_fav_outcome,
                "favourable_outcome": number_unpriviliged_with_fav_outcome},
            1: {"favourable_outcome": number_priviliged_with_fav_outcome,
                "favourable_outcome": number_priviliged_with_fav_outcome},
            "disparity": statistical_disparity_over_priv_and_unpriv_group
        }

    clf: A classifier with a `predict()` function.
    data: A pandas dataframe containing each of the listed `group_names`.
    group_names: A list of column names defining sensitive attributes.
    ground_truth:
        Assumes 1 as favourable outcome and 0 as unfavourable outcome.
    """
    test_set = data.copy(deep=True)

    outcol = "Outcome"
    cols = test_set.columns
    while outcol in cols:
        outcol += "_" # We add _ as long as we need to to get a unique name.

    test_set[outcol] = clf.predict(test_set.drop([ground_truth], axis=1)) # Predictions

    return predictive_equality(test_set, group_names, ground_truth, outcol, fav_label=fav_label)


def equality_of_opportunity(df, group_names, ground_truth, outcome_name, fav_label=1):
    """
    Assesses the fairness in the dataframe over the given groups.
    Returns a map containing an entry for each specified group in `group_names`.
    For a group G, the entries are:

        result[G] = {
            0: {"favourable_outcome": number_unpriviliged_with_fav_outcome,
                "favourable_outcome": number_unpriviliged_with_fav_outcome},
            1: {"favourable_outcome": number_priviliged_with_fav_outcome,
                "favourable_outcome": number_priviliged_with_fav_outcome},
            "disparity": statistical_disparity_over_priv_and_unpriv_group
        }

    df: A pandas dataframe ccontaining the column `outcome_name` and each of the
        listed `group_names`.
    group_names: A list of column names defining sensitive attributes.
    ground_truth: Name of the column corresponding to the ground truth value.
        Assumes 1 as favourable outcome and 0 as unfavourable outcome.
    outcome_name: Name of the column corresponding to the outcome. Assumes 1 as
        favourable outcome and 0 as unfavourable outcome.
    """

    fairnesses = {}
    for group in group_names:
        fair = {}

        priv = df[(df[group] == 1) & (df[ground_truth]==fav_label)]
        unpriv = df[(df[group] != 1) & (df[ground_truth]==fav_label)]

        priv_fav = len(priv[priv[outcome_name] == fav_label])
        priv_unfav = len(priv[priv[outcome_name] != fav_label])
        unpriv_fav = len(unpriv[unpriv[outcome_name] == fav_label])
        unpriv_unfav = len(unpriv[unpriv[outcome_name] != fav_label])

        fair[1] = {"favourable_outcome": priv_fav,
                   "unfavourable_outcome": priv_unfav}
        fair[0] = {"favourable_outcome": unpriv_fav,
                   "unfavourable_outcome": unpriv_unfav}
        fair["disparity"] = priv_unfav/len(priv) - unpriv_unfav/len(unpriv)

        fairnesses[group] = fair

    return fairnesses



def clf_equality_of_opportunity(clf, data, ground_truth, group_names, fav_label=1):
    """
    Assesses the fairness of the give classiier over the dataframe per  group.
    Returns a map containing an entry for each specified group in `group_names`.
    For a group G, the entries are:

        result[G] = {
            0: {"favourable_outcome": number_unpriviliged_with_fav_outcome,
                "favourable_outcome": number_unpriviliged_with_fav_outcome},
            1: {"favourable_outcome": number_priviliged_with_fav_outcome,
                "favourable_outcome": number_priviliged_with_fav_outcome},
            "disparity": statistical_disparity_over_priv_and_unpriv_group
        }

    clf: A classifier with a `predict()` function.
    data: A pandas dataframe containing each of the listed `group_names`.
    group_names: A list of column names defining sensitive attributes.
    ground_truth:
        Assumes 1 as favourable outcome and 0 as unfavourable outcome.
    """
    test_set = data.copy(deep=True)

    outcol = "Outcome"
    cols = test_set.columns
    while outcol in cols:
        outcol += "_" # We add _ as long as we need to to get a unique name.

    test_set[outcol] = clf.predict(test_set.drop([ground_truth], axis=1)) # Predictions

    return equality_of_opportunity(test_set, group_names, ground_truth, outcol, fav_label=fav_label)
