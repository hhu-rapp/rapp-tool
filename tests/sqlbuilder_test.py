from json import loads
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
