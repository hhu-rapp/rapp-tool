import pytest

from rapp import sqlbuilder
from rapp.sqlbuilder import load_sql, list_available_features, list_available_labels

from tests import resources as rc

@pytest.fixture(autouse=True)
def reset_loaded_db():
    yield  # Execute test.
    sqlbuilder._LOADEDDB = None

@pytest.fixture(autouse=True)
def set_default_template_path():
    old_default = sqlbuilder._DEFAULTTEMPLATEDIR
    sqlbuilder._DEFAULTTEMPLATEDIR = rc.get_path("sql/db_specific_templates")
    yield  # Execute test.
    sqlbuilder._DEFAULTTEMPLATEDIR = old_default



def test_listing_available_features_without_loaded_db():
    expected = ['non_specific_1',
                'non_specific_2',
                ]
    actual = list_available_features()

    assert expected == actual


def test_listing_available_features_with_loaded_rapp_db():
    sqlbuilder._LOADEDDB = 'rapp.db'

    expected = ['non_specific_1',
                'non_specific_2',
                'rapp_specific_1',
                'rapp_specific_2',
                'rapp_specific_3',
                ]
    actual = list_available_features()

    sqlbuilder._LOADEDDB = None
    assert expected == actual


def test_listing_available_features_with_loaded_other_db():
    sqlbuilder._LOADEDDB = 'other.db'

    expected = ['non_specific_1',
                'non_specific_2',
                'other_features_1',
                ]
    actual = list_available_features()

    sqlbuilder._LOADEDDB = None
    assert expected == actual


def test_listing_available_labels_without_loaded_db():
    expected = ['general_label_1',
                'shadow_label',
                ]
    actual = list_available_labels()

    assert expected == actual


def test_listing_available_labels_with_loaded_rapp_db():
    sqlbuilder._LOADEDDB = 'rapp.db'

    expected = ['general_label_1',
                'rapp_label_1',
                'rapp_label_2',
                'shadow_label',
                ]
    actual = list_available_labels()

    assert expected == actual


def test_listing_available_labels_with_loaded_other_db():
    sqlbuilder._LOADEDDB = 'other.db'

    expected = ['general_label_1',
                'other_label_1',
                'other_label_2',
                'shadow_label',
                ]
    actual = list_available_labels()

    assert expected == actual


def test_loading_db_specific_sql():
    sqlbuilder._LOADEDDB = 'rapp.db'

    # 'cs_first_term_modules' and '3_dropout' correspond to
    # rapp.de/features/rapp_specific_1 and general_label_1 respectively.
    expected = rc.get_text("sql/cs_first_term_modules_dropout.sql")
    actual = load_sql("rapp_specific_1", "general_label_1")

    assert expected == actual


def test_shadowing_general_snippet_by_db_specific_one():
    sqlbuilder._LOADEDDB = 'other.db'

    # 'cs_first_term_modules' and '3_dropout' correspond to
    # rapp.de/features/rapp_specific_1 and general_label_1 respectively.
    expected = rc.get_text("sql/cs_first_term_modules_dropout.sql")
    actual = load_sql("non_specific_1", "shadow_label")

    assert expected == actual
