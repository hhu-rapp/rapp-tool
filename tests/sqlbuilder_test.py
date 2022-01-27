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

    db_conn = testutil.get_db_connection()

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
    # Setup database
    db = testutil.TestDb(empty=True)
    db.add_modules(("a", 1, 1),
                   ("b", 1, 2),
                   ("c", 1, 3))
    s1 = db.add_ifo_student(pseudonym=1)

    # "a" passed first try
    db.add_exam(s1, "a", attempt=1, semester=1, passed=True, ects=5, grade=1.0)
    # "b" passed third try
    db.add_exam(s1, "b", attempt=1, semester=1)
    db.add_exam(s1, "b", attempt=2, semester=1)
    db.add_exam(s1, "b", attempt=3, semester=1, passed=True, ects=10, grade=2.0)
    # "c" passed in second term
    db.add_exam(s1, "c", attempt=1, semester=3, passed=True, ects=10, grade=3.0)

    sql = load_sql("cs_first_term_ects", "4term_cp")

    df = db.read_sql_query(sql)
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
        "EctsPerExam": 15/4,
        "FourthTermCP": 0
    }

    assert expected == actual


def test_cs_ects_features__when_no_passed_exams():
    # Setup database
    db = testutil.TestDb(empty=True)
    db.add_modules(("a", 1, 1),
                   ("b", 1, 2),
                   ("c", 1, 3))
    s1 = db.add_ifo_student(pseudonym=1)

    # "b" failed twice
    db.add_exam(s1, "b", attempt=1, semester=1)
    db.add_exam(s1, "b", attempt=2, semester=1)
    # "c" passed in second term
    db.add_exam(s1, "c", attempt=1, semester=3, passed=True, ects=10, grade=3.0)

    sql = load_sql("cs_first_term_ects", "4term_cp")
    df = db.read_sql_query(sql)
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
        "EctsPerExam": 0,
        "FourthTermCP": 0
    }

    assert expected == actual


def test_cs_ects_features__when_no_written_exams():
    # Setup database
    db = testutil.TestDb(empty=True)
    db.add_modules(("a", 1, 1),
                   ("b", 1, 2),
                   ("c", 1, 3))
    s1 = db.add_ifo_student(pseudonym=1)

    # "c" passed in second term
    db.add_exam(s1, "c", attempt=1, semester=3, passed=True, ects=10, grade=3.0)

    sql = load_sql("cs_first_term_ects", "4term_cp")
    df = db.read_sql_query(sql)

    assert len(df) == 0


def test_cs_unspecific_grade_features():
    # Setup database
    db = testutil.TestDb(empty=True)
    db.add_modules(("a", 1, 1),
                   ("b", 1, 2),
                   ("c", 1, 3))
    s1 = db.add_ifo_student(pseudonym=1)

    # "a" passed first try
    db.add_exam(s1, "a", attempt=1, semester=1, passed=True, ects=5, grade=1.0)
    # "b" passed third try
    db.add_exam(s1, "b", attempt=1, semester=1)
    db.add_exam(s1, "b", attempt=2, semester=1)
    db.add_exam(s1, "b", attempt=3, semester=1, passed=True, ects=10, grade=3.0)
    # "c" passed in second term
    db.add_exam(s1, "c", attempt=1, semester=3, passed=True, ects=10, grade=3.0)

    sql = load_sql("cs_first_term_grades", "4term_cp")
    df = db.read_sql_query(sql)
    actual = df.to_dict(orient='records')[0]  # Only compare first entry here.

    expected = {
        "Geschlecht": "männlich",
        "Deutsch": 1,
        "AlterEinschreibung": 21,
        "KlausurenGeschrieben": 4,
        "KlausurenBestanden": 2,
        "KlausurenNichtBestanden": 2,
        "DurchschnittsnoteBestanden": 2,
        "DurchschnittsnoteTotal": 14/4,
        "VarianzNoteBestanden": 1.,
        "VarianzNoteTotal": 2.75,
        "PassedExamsRatio": 0.5,
        "FourthTermCP": 0,
    }

    assert expected == actual


def test_combined_ectp_grade_features():
    # Setup database
    db = testutil.TestDb(empty=True)
    db.add_modules(("a", 1, 1),
                   ("b", 1, 2),
                   ("c", 1, 3))
    s1 = db.add_ifo_student(pseudonym=1)

    # "a" passed first try
    db.add_exam(s1, "a", attempt=1, semester=1, passed=True, ects=5, grade=1.0)
    # "b" passed third try
    db.add_exam(s1, "b", attempt=1, semester=1)
    db.add_exam(s1, "b", attempt=2, semester=1)
    db.add_exam(s1, "b", attempt=3, semester=1, passed=True, ects=10, grade=3.0)
    # "c" passed in second term
    db.add_exam(s1, "c", attempt=1, semester=3, passed=True, ects=10, grade=3.0)

    sql = load_sql("cs_first_term_grades_and_ectp", "4term_cp")
    df = db.read_sql_query(sql)
    actual = df.to_dict(orient='records')[0]  # Only compare first entry here.

    expected = {
        "Geschlecht": "männlich",
        "Deutsch": 1,
        "AlterEinschreibung": 21,
        "Ectp": 15,
        "KlausurenGeschrieben": 4,
        "KlausurenBestanden": 2,
        "KlausurenNichtBestanden": 2,
        "DurchschnittsnoteBestanden": 2,
        "DurchschnittsnoteTotal": 14/4,
        "VarianzNoteBestanden": 1.,
        "VarianzNoteTotal": 2.75,
        "PassedExamsRatio": 0.5,
        "EctpPerExam": 15/4,
        "FourthTermCP": 0,
    }

    assert expected == actual


def test_combined_ectp_and_grade_should_have_same_ectp_as_ectp_only_features():
    sql_combined = load_sql("cs_first_term_grades_and_ectp", "4term_cp")
    sql_ectp = load_sql("cs_first_term_ects", "4term_cp")

    db = testutil.get_db_connection()

    df = read_sql_query(sql_ectp, db)
    # Ensure equal column names
    df = df.rename(columns={"EctsFirstTerm": "Ectp"})
    ectp_only = df["Ectp"]

    df = read_sql_query(sql_combined, db)
    combined = df["Ectp"]

    assert (ectp_only == combined).all()


def test_combined_ectp_and_grade_should_have_same_grades_as_grade_only_features():
    sql_combined = load_sql("cs_first_term_grades_and_ectp", "4term_cp")
    sql_grades = load_sql("cs_first_term_grades", "4term_cp")

    db = testutil.get_db_connection()

    df = read_sql_query(sql_grades, db)
    grade_only = df[["DurchschnittsnoteBestanden", "DurchschnittsnoteTotal"]]

    df = read_sql_query(sql_combined, db)
    combined = df[["DurchschnittsnoteBestanden", "DurchschnittsnoteTotal"]]

    assert grade_only.equals(combined)


def test_sw_base_module_regression():
    regression_test_setup(
        feature="sw_second_term_base_modules",
        label="3_dropout",
        reference="sw_base_modules_dropout.sql")
