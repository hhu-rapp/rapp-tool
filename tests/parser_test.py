from rapp.parser import RappConfigParser
import pytest

import tests.resources as rc


def test_basic_call():
    ini_file = rc.get_path('empty.ini')
    args = f"-cf {ini_file} -f db.db -sid cs -fid feats -lid labels --label_name target"
    parser = RappConfigParser()
    cf = parser.parse_args(args)

    assert (cf.filename == "db.db"
            and cf.studies_id == 'cs'
            and cf.features_id == 'feats'
            and cf.labels_id == 'labels'
            and cf.label_name == 'target')


def test_categorical_always_set():
    ini_file = rc.get_path('empty.ini')
    args = f"-cf {ini_file} -f db.db -sid cs -fid feats -lid labels --label_name target"
    parser = RappConfigParser()
    cf = parser.parse_args(args)

    assert cf.categorical == []


def test_sql_file_call():
    ini_file = rc.get_path('empty.ini')
    args = f"-cf {ini_file} -f db.db -sf foo.sql --label_name target"
    parser = RappConfigParser()
    cf = parser.parse_args(args)

    assert cf.sql_file == "foo.sql"


def test_sql_file_and_templating_ids_simultaneously():
    ini_file = rc.get_path('empty.ini')
    args = f"-cf {ini_file} -f db.db -sf foo.sql -sid cs -fid feats -lid labels --label_name target"
    parser = RappConfigParser()

    with pytest.raises(Exception):
        parser.parse_args(args)


def test_only_studies_id_for_templating():
    ini_file = rc.get_path('empty.ini')
    args = f"-cf {ini_file} -f db.db -sid cs --label_name target"
    parser = RappConfigParser()

    with pytest.raises(Exception):
        parser.parse_args(args)


def test_only_labels_id_for_templating():
    ini_file = rc.get_path('empty.ini')
    args = f"-cf {ini_file} -f db.db -lid labels --label_name target"
    parser = RappConfigParser()

    with pytest.raises(Exception):
        parser.parse_args(args)


def test_only_features_id_for_templating():
    ini_file = rc.get_path('empty.ini')
    args = f"-cf {ini_file} -f db.db -fid features --label_name target"
    parser = RappConfigParser()

    with pytest.raises(Exception):
        parser.parse_args(args)


def test_missing_features_id_for_templating():
    ini_file = rc.get_path('empty.ini')
    args = f"-cf {ini_file} -f db.db -sid cs -lid labels --label_name target"
    parser = RappConfigParser()

    with pytest.raises(Exception):
        parser.parse_args(args)


def test_missing_studies_id_for_templating():
    ini_file = rc.get_path('empty.ini')
    args = f"-cf {ini_file} -f db.db -fid features -lid labels --label_name target"
    parser = RappConfigParser()

    with pytest.raises(Exception):
        parser.parse_args(args)


def test_missing_labels_id_for_templating():
    ini_file = rc.get_path('empty.ini')
    args = f"-cf {ini_file} -f db.db -sid cs -fid features --label_name target"
    parser = RappConfigParser()

    with pytest.raises(Exception):
        parser.parse_args(args)


def test_sql_query_and_templating_ids_simultaneously():
    ini_file = rc.get_path('empty.ini')
    args = f"-cf {ini_file} -f db.db -sq select -sid cs -fid feats -lid labels --label_name target"
    parser = RappConfigParser()

    with pytest.raises(Exception):
        parser.parse_args(args)


def test_sql_file_and_query_simultaneously():
    ini_file = rc.get_path('empty.ini')
    args = f"-cf {ini_file} -f db.db -sf foo.sql -sq query --label_name target"
    parser = RappConfigParser()

    with pytest.raises(Exception):
        parser.parse_args(args)


def test_no_sql_info_at_all():
    ini_file = rc.get_path('empty.ini')
    args = f"-cf {ini_file} -f db.db --label_name target"
    parser = RappConfigParser()

    with pytest.raises(Exception):
        parser.parse_args(args)


def test_direct_sql_query():
    ini_file = rc.get_path('empty.ini')
    args = ["-cf", ini_file, "-f", "db.db", "-sq", "select *",
            "--label_name", "target"]
    parser = RappConfigParser()
    cf = parser.parse_args(args)

    assert cf.sql_query == 'select *'


def test_config_file_is_optional():
    args = f"-f db.db -sf foo.sql --label_name target"
    parser = RappConfigParser()

    try:
        _ = parser.parse_args(args)
    except Exception as e:
        pytest.fail(f"Should be able to parse arguments when no config file"
                    f"is given, but threw exception: {e}")
    except SystemExit as e:
        pytest.fail(f"Should be able to parse arguments when no config file"
                    f"is given, but ended in SystemExit {e}")
