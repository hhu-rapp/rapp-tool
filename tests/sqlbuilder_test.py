from pandas import read_sql_query

from rapp.sqlbuilder import load_sql

from tests import resources as rc
from tests import testutil


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


def test_cs_ects_features():
    # Setup 3 modules
    modules = [
        {"version": 1, "nummer": 1, "modul": "a"},
        {"version": 1, "nummer": 2, "modul": "b"},
        {"version": 1, "nummer": 3, "modul": "c"},
    ]

    # Student 1
    s1 = {
        "einschreibung": {"pseudonym": 1},
        "student": {"pseudonym": 1},
        "ssp": [
            # "a" passed first try
            {"pseudonym": 1, "version": 1, "nummer": 1,
             "status": "bestanden", "note": 1.0, "ects": 5,
             "fachsemester": 1},
            # "b" passed third try
            {"pseudonym": 1, "version": 1, "nummer": 2,
             "status": "nicht bestanden", "note": 5.0, "ects": 0,
             "fachsemester": 1},
            {"pseudonym": 1, "version": 1, "nummer": 2,
             "status": "nicht bestanden", "note": 5.0, "ects": 0,
             "versuch": 2, "fachsemester": 1},
            {"pseudonym": 1, "version": 1, "nummer": 2,
             "status": "bestanden", "note": 2.0, "ects": 10,
             "versuch": 3, "fachsemester": 1},
            # "c" passed in second term
            {"pseudonym": 1, "version": 1, "nummer": 2,
             "status": "bestanden", "note": 3.0, "ects": 10,
             "versuch": 1, "fachsemester": 2},
        ],
    }

    # Populate db
    db = testutil.get_empty_memory_db_connection()
    for m in modules:
        testutil.insert_into_Pruefung(db, **m)
    testutil.insert_into_Einschreibung(db, **s1["einschreibung"])
    testutil.insert_into_Student(db, **s1["student"])
    for ssp in s1["ssp"]:
        testutil.insert_into_Student_schreibt_Pruefung(db, **ssp)

    sql = load_sql("cs_first_term_ects", "4term_cp")

    df = read_sql_query(sql, db)
    actual = df.to_dict(orient='records')[0]  # Only compare first entry here.

    expected = {
        "Geschlecht": "männlich",
        "Deutsch": 1,
        "AlterEinschreibung": 21,
        "EctsFirstTerm": 15,
        "ExamsFirstTerm": 4,
        "PassedFirstTerm": 2,
        "FailedFirstTerm": 2,
        "PassedExamsRatio": 0.5,
        "FourthTermCP": 0
    }

    assert expected == actual


def test_cs_ects_features__when_no_passed_exams():
    # Setup 3 modules
    modules = [
        {"version": 1, "nummer": 1, "modul": "a"},
        {"version": 1, "nummer": 2, "modul": "b"},
        {"version": 1, "nummer": 3, "modul": "c"},
    ]

    # Student 1
    s1 = {
        "einschreibung": {"pseudonym": 1},
        "student": {"pseudonym": 1},
        "ssp": [
            # "b" failed twice
            {"pseudonym": 1, "version": 1, "nummer": 2,
             "status": "nicht bestanden", "note": 5.0, "ects": 0,
             "fachsemester": 1},
            {"pseudonym": 1, "version": 1, "nummer": 2,
             "status": "nicht bestanden", "note": 5.0, "ects": 0,
             "versuch": 2, "fachsemester": 1},
            # "c" passed in second term
            {"pseudonym": 1, "version": 1, "nummer": 2,
             "status": "bestanden", "note": 3.0, "ects": 10,
             "versuch": 1, "fachsemester": 2},
        ],
    }

    # Populate db
    db = testutil.get_empty_memory_db_connection()
    for m in modules:
        testutil.insert_into_Pruefung(db, **m)
    testutil.insert_into_Einschreibung(db, **s1["einschreibung"])
    testutil.insert_into_Student(db, **s1["student"])
    for ssp in s1["ssp"]:
        testutil.insert_into_Student_schreibt_Pruefung(db, **ssp)

    sql = load_sql("cs_first_term_ects", "4term_cp")

    df = read_sql_query(sql, db)
    actual = df.to_dict(orient='records')[0]  # Only compare first entry here.

    expected = {
        "Geschlecht": "männlich",
        "Deutsch": 1,
        "AlterEinschreibung": 21,
        "EctsFirstTerm": 0,
        "ExamsFirstTerm": 2,
        "PassedFirstTerm": 0,
        "FailedFirstTerm": 2,
        "PassedExamsRatio": 0.,
        "FourthTermCP": 0
    }

    assert expected == actual


def test_cs_ects_features__when_no_written_exams():
    # Setup 3 modules
    modules = [
        {"version": 1, "nummer": 1, "modul": "a"},
        {"version": 1, "nummer": 2, "modul": "b"},
        {"version": 1, "nummer": 3, "modul": "c"},
    ]

    # Student 1
    s1 = {
        "einschreibung": {"pseudonym": 1},
        "student": {"pseudonym": 1},
        "ssp": [
            # "c" passed in second term
            {"pseudonym": 1, "version": 1, "nummer": 2,
             "status": "bestanden", "note": 3.0, "ects": 10,
             "versuch": 1, "fachsemester": 2},
        ],
    }

    # Populate db
    db = testutil.get_empty_memory_db_connection()
    for m in modules:
        testutil.insert_into_Pruefung(db, **m)
    testutil.insert_into_Einschreibung(db, **s1["einschreibung"])
    testutil.insert_into_Student(db, **s1["student"])
    for ssp in s1["ssp"]:
        testutil.insert_into_Student_schreibt_Pruefung(db, **ssp)

    sql = load_sql("cs_first_term_ects", "4term_cp")

    df = read_sql_query(sql, db)
    actual = df.to_dict(orient='records')[0]  # Only compare first entry here.

    expected = {
        "Geschlecht": "männlich",
        "Deutsch": 1,
        "AlterEinschreibung": 21,
        "EctsFirstTerm": 0,
        "ExamsFirstTerm": 0,
        "PassedFirstTerm": 0,
        "FailedFirstTerm": 0,
        "PassedExamsRatio": 0.,
        "FourthTermCP": 0
    }

    assert expected == actual
