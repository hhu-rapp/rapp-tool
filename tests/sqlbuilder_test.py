from hmac import new
from pandas import read_sql_query

from rapp.sqlbuilder import load_sql

from tests import resources as rc


def test_construct_when_all_parts_are_given():
    """
    Both, features and label, have each a select, join, and where statement
    that is given in the templates.
    """
    expected = rc.get_text("sql/cs_first_term_modules_dropout.sql")
    actual = load_sql("cs_first_term_modules", "3_dropout")

    assert expected == actual


def test_construct_when_join_and_where_is_missing():
    """
    The label 4_term_ap has no JOIN or WHERE information.
    """
    expected = rc.get_text("sql/cs_first_term_modules_4term_ap.sql")
    actual = load_sql("cs_first_term_modules", "4term_ap")

    print(actual)
    assert expected == actual


def regression_test_setup(feature, label, reference):
    """
    Boilerplate template for testing whether the modular SQL system
    creates semantically equivalent SQL queries to those we had before.
    """
    old_sql = rc.get_text("sql/regression/" + reference)
    new_sql = load_sql(feature, label)

    db_conn = rc.get_db_connection()

    old_results = read_sql_query(old_sql, db_conn)
    new_results = read_sql_query(new_sql, db_conn)

    assert new_results.equals(old_results)


def test_dropout_regression():
    regression_test_setup(
        feature="cs_first_term_modules",
        label="3_dropout",
        reference="cs-first_term_modules-3_dropout.sql")


def test_master_admission_regression():
    regression_test_setup(
        feature="cs_first_term_modules",
        label="master_admission",
        reference="cs-first_term_modules-master_admission.sql")


def test_4term_cp_regression():
    regression_test_setup(
        feature="cs_first_term_modules",
        label="4term_cp",
        reference="cs-first_term_modules-4term_ectp.sql")


def test_4term_ap_regression():
    regression_test_setup(
        feature="cs_first_term_modules",
        label="4term_ap",
        reference="cs-first_term_modules-4term_ap.sql")


def test_rsz_regression():
    regression_test_setup(
        feature="cs_first_term_modules",
        label="rsz",
        reference="cs-first_term_modules-rsz.sql")
