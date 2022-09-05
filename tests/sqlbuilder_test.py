import pytest
from pandas import read_sql_query

from rapp import sqlbuilder
from rapp.sqlbuilder import load_sql, list_available_features, list_available_labels

from tests import resources as rc
from tests import testutil


DIR=rc.get_path("sql/templatesous")

@pytest.fixture(autouse=True)
def set_default_template_path():
    old_default = sqlbuilder._DEFAULTTEMPLATEDIR
    sqlbuilder._DEFAULTTEMPLATEDIR = rc.get_path('sql/templates')
    yield  # Execute test.
    sqlbuilder._DEFAULTTEMPLATEDIR = old_default



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
    s2 = db.add_sw_student(pseudonym=2)  # Non-CS student to be ignored.

    # "a" passed first try
    db.add_exam(s1, "a", attempt=1, semester=1, passed=True, ects=5, grade=1.0)
    db.add_exam(s2, "a", attempt=1, semester=1, passed=True, ects=5, grade=1.0)
    # "b" passed third try
    db.add_exam(s1, "b", attempt=1, semester=1)
    db.add_exam(s1, "b", attempt=2, semester=1)
    db.add_exam(s1, "b", attempt=3, semester=1,
                passed=True, ects=10, grade=2.0)
    # "c" passed in second term
    db.add_exam(s1, "c", attempt=1, semester=3,
                passed=True, ects=10, grade=3.0)

    sql = load_sql("cs_first_term_ects", "4term_cp")

    df = db.read_sql_query(sql)
    actual = df.to_dict(orient='records')

    expected = [{
        "Geschlecht": "männlich",
        "Deutsch": 1,
        "AlterEinschreibung": 21,
        "EctsFirstTerm": 15,
        "ExamsFirstTerm": 4,
        "PassedFirstTerm": 2,
        "FailedFirstTerm": 2,
        "PassedExamsRatio": 0.5,
        "EctsPerExam": 15 / 4,
        "FourthTermCP": 0
    }]

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
    db.add_exam(s1, "c", attempt=1, semester=3,
                passed=True, ects=10, grade=3.0)

    # Non-CS student to be ignored.
    s2 = db.add_sw_student(pseudonym=2)
    db.add_exam(s2, "a", attempt=1, semester=1, passed=True, ects=5, grade=1.0)

    sql = load_sql("cs_first_term_ects", "4term_cp")
    df = db.read_sql_query(sql)
    actual = df.to_dict(orient='records')

    expected = [{
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
    }]

    assert expected == actual


def test_cs_ects_features__when_no_written_exams():
    # Setup database
    db = testutil.TestDb(empty=True)
    db.add_modules(("a", 1, 1),
                   ("b", 1, 2),
                   ("c", 1, 3))
    s1 = db.add_ifo_student(pseudonym=1)

    # "c" passed in second term
    db.add_exam(s1, "c", attempt=1, semester=3,
                passed=True, ects=10, grade=3.0)

    # Non-CS student to be ignored.
    s2 = db.add_sw_student(pseudonym=2)
    db.add_exam(s2, "a", attempt=1, semester=1, passed=True, ects=5, grade=1.0)

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
    db.add_exam(s1, "b", attempt=3, semester=1,
                passed=True, ects=10, grade=3.0)
    # "c" passed in second term
    db.add_exam(s1, "c", attempt=1, semester=3,
                passed=True, ects=10, grade=3.0)

    # Non-CS student to be ignored.
    s2 = db.add_sw_student(pseudonym=2)
    db.add_exam(s2, "a", attempt=1, semester=1, passed=True, ects=5, grade=1.0)

    sql = load_sql("cs_first_term_grades", "4term_cp")
    df = db.read_sql_query(sql)
    actual = df.to_dict(orient='records')

    expected = [{
        "Geschlecht": "männlich",
        "Deutsch": 1,
        "AlterEinschreibung": 21,
        "KlausurenGeschrieben": 4,
        "KlausurenBestanden": 2,
        "KlausurenNichtBestanden": 2,
        "DurchschnittsnoteBestanden": 2,
        "DurchschnittsnoteTotal": 14 / 4,
        "VarianzNoteBestanden": 1.,
        "VarianzNoteTotal": 2.75,
        "PassedExamsRatio": 0.5,
        "FourthTermCP": 0,
    }]

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
    db.add_exam(s1, "b", attempt=3, semester=1,
                passed=True, ects=10, grade=3.0)
    # "c" passed in second term
    db.add_exam(s1, "c", attempt=1, semester=3,
                passed=True, ects=10, grade=3.0)

    # Non-CS student to be ignored.
    s2 = db.add_sw_student(pseudonym=2)
    db.add_exam(s2, "a", attempt=1, semester=1, passed=True, ects=5, grade=1.0)

    sql = load_sql("cs_first_term_grades_and_ectp", "4term_cp")
    df = db.read_sql_query(sql)
    actual = df.to_dict(orient='records')

    expected = [{
        "Geschlecht": "männlich",
        "Deutsch": 1,
        "AlterEinschreibung": 21,
        "Ectp": 15,
        "KlausurenGeschrieben": 4,
        "KlausurenBestanden": 2,
        "KlausurenNichtBestanden": 2,
        "DurchschnittsnoteBestanden": 2,
        "DurchschnittsnoteTotal": 14 / 4,
        "VarianzNoteBestanden": 1.,
        "VarianzNoteTotal": 2.75,
        "PassedExamsRatio": 0.5,
        "EctpPerExam": 15 / 4,
        "FourthTermCP": 0,
    }]

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


def test_sw_first_term_ects():
    # Setup database
    db = testutil.TestDb(empty=True)
    db.add_modules(("a", 1, 1),
                   ("b", 1, 2),
                   ("c", 1, 3))
    s1 = db.add_sw_student(pseudonym=1)
    s2 = db.add_ifo_student(pseudonym=2)  # CS student

    # "a" passed first try
    db.add_exam(s1, "a", attempt=1, semester=1, passed=True, ects=5, grade=1.0)
    db.add_exam(s2, "a", attempt=1, semester=1, passed=True, ects=5, grade=1.0)
    # "b" passed third try
    db.add_exam(s1, "b", attempt=1, semester=1)
    db.add_exam(s1, "b", attempt=2, semester=1)
    db.add_exam(s1, "b", attempt=3, semester=1,
                passed=True, ects=10, grade=2.0)
    # "c" passed in second term
    db.add_exam(s1, "c", attempt=1, semester=3,
                passed=True, ects=10, grade=3.0)

    sql = load_sql("sw_first_term_ects", "4term_cp")

    df = db.read_sql_query(sql)
    actual = df.to_dict(orient='records')

    expected = [{
        "Geschlecht": "männlich",
        "Deutsch": 1,
        "AlterEinschreibung": 21,
        "EctsFirstTerm": 15,
        "ExamsFirstTerm": 4,
        "PassedFirstTerm": 2,
        "FailedFirstTerm": 2,
        "PassedExamsRatio": 0.5,
        "EctsPerExam": 15 / 4,
        "FourthTermCP": 0
    }]

    assert expected == actual


def test_sw_first_term_grades():
    # Setup database
    db = testutil.TestDb(empty=True)
    db.add_modules(("a", 1, 1),
                   ("b", 1, 2),
                   ("c", 1, 3))
    s1 = db.add_sw_student(pseudonym=1)
    s2 = db.add_ifo_student(pseudonym=2)  # CS Student to be ignored.

    # "a" passed first try
    db.add_exam(s1, "a", attempt=1, semester=1, passed=True, ects=5, grade=1.0)
    db.add_exam(s2, "a", attempt=1, semester=1, passed=True, ects=5, grade=1.0)
    # "b" passed third try
    db.add_exam(s1, "b", attempt=1, semester=1)
    db.add_exam(s1, "b", attempt=2, semester=1)
    db.add_exam(s1, "b", attempt=3, semester=1,
                passed=True, ects=10, grade=3.0)
    # "c" passed in second term
    db.add_exam(s1, "c", attempt=1, semester=3,
                passed=True, ects=10, grade=3.0)

    sql = load_sql("sw_first_term_grades", "4term_cp")

    df = db.read_sql_query(sql)
    actual = df.to_dict(orient='records')  # Only compare first entry here.

    expected = [{
        "Geschlecht": "männlich",
        "Deutsch": 1,
        "AlterEinschreibung": 21,
        "KlausurenGeschrieben": 4,
        "KlausurenBestanden": 2,
        "KlausurenNichtBestanden": 2,
        "DurchschnittsnoteBestanden": 2,
        "DurchschnittsnoteTotal": 14 / 4,
        "VarianzNoteBestanden": 1.,
        "VarianzNoteTotal": 2.75,
        "PassedExamsRatio": 0.5,
        "FourthTermCP": 0,
    }]

    assert expected == actual


def test_sw_first_term_combined_ects_and_grades():
    # Setup database
    db = testutil.TestDb(empty=True)
    db.add_modules(("a", 1, 1),
                   ("b", 1, 2),
                   ("c", 1, 3))
    s1 = db.add_sw_student(pseudonym=1)
    s2 = db.add_ifo_student(pseudonym=2)  # CS Student to be ignored.

    # "a" passed first try
    db.add_exam(s1, "a", attempt=1, semester=1, passed=True, ects=5, grade=1.0)
    db.add_exam(s2, "a", attempt=1, semester=1, passed=True, ects=5, grade=1.0)
    # "b" passed third try
    db.add_exam(s1, "b", attempt=1, semester=1)
    db.add_exam(s1, "b", attempt=2, semester=1)
    db.add_exam(s1, "b", attempt=3, semester=1,
                passed=True, ects=10, grade=3.0)
    # "c" passed in second term
    db.add_exam(s1, "c", attempt=1, semester=3,
                passed=True, ects=10, grade=3.0)

    sql = load_sql("sw_first_term_grades_and_ectp", "4term_cp")

    df = db.read_sql_query(sql)
    actual = df.to_dict(orient='records')  # Only compare first entry here.

    expected = [{
        "Geschlecht": "männlich",
        "Deutsch": 1,
        "AlterEinschreibung": 21,
        "Ectp": 15,
        "KlausurenGeschrieben": 4,
        "KlausurenBestanden": 2,
        "KlausurenNichtBestanden": 2,
        "DurchschnittsnoteBestanden": 2,
        "DurchschnittsnoteTotal": 14 / 4,
        "VarianzNoteBestanden": 1.,
        "VarianzNoteTotal": 2.75,
        "PassedExamsRatio": 0.5,
        "EctpPerExam": 15 / 4,
        "FourthTermCP": 0,
    }]

    assert expected == actual


def test_study_duration_labels_as_classification_problem():
    """
    See discussion to commit #925bfe64
    - https://gitlab.cs.uni-duesseldorf.de/dbs/research/project/rapp/rapp-gui/-/commit/925bfe64dbdea6d3d823bb86746d590d6ee628d1
    """
    # Setup database
    db = testutil.TestDb(empty=True)
    db.add_modules(("a", 1, 1), ("b", 1, 2) )

    # Students that are identical but have different study duration
    students = []
    for i in range(0, 15): # 15 students, pseudonyms 0..14
        cs_student = db.add_ifo_student(pseudonym=i, bestanden=1)
        students.append(cs_student)

        # Exam a is passed in first term: everyone has equal first term data
        db.add_exam(cs_student, 'a', attempt=1, semester=1, passed=True, ects=5, grade=1.0)

        # Exam b is passed in final term, which is different for each student
        ## semester of last exam is used to determine final study duration
        ## Skip student #0 which would have exam 'b' in semester 1 as well;
        ## exam 'a' is sufficient for this test then.
        if i > 0:
            db.add_exam(cs_student, 'b', attempt=1, semester=(i+1), passed=True, ects=5, grade=1.0)

    sql = load_sql("cs_first_term_ects", "study_duration")

    df = db.read_sql_query(sql)
    actual = df.to_dict(orient='records')

    # Study duration class labels to be distributed, in order:
    labels = [4, 4, 4, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 10, 10]
    expected = [{
        "Geschlecht": "männlich",
        "Deutsch": 1,
        "AlterEinschreibung": 21,
        "EctsFirstTerm": 5,
        "ExamsFirstTerm": 1,
        "PassedFirstTerm": 1,
        "FailedFirstTerm": 0,
        "PassedExamsRatio": 1.,
        "EctsPerExam": 5,
        "StudyDuration": duration
    } for duration in labels]

    assert expected == actual


@pytest.mark.skip(reason="We do not have any SW students in the test DB as of now.")
def test_sw_combined_ectp_and_grade_should_have_same_ectp_as_ectp_only_features():
    sql_combined = load_sql("sw_first_term_grades_and_ectp", "4term_cp")
    sql_ectp = load_sql("sw_first_term_ects", "4term_cp")

    db = testutil.get_db_connection()

    df = read_sql_query(sql_ectp, db)
    # Ensure equal column names
    df = df.rename(columns={"EctsFirstTerm": "Ectp"})
    ectp_only = df["Ectp"]

    df = read_sql_query(sql_combined, db)
    combined = df["Ectp"]

    assert (ectp_only == combined).all()


@pytest.mark.skip(reason="We do not have any SW students in the test DB as of now.")
def test_sw_combined_ectp_and_grade_should_have_same_grades_as_grade_only_features():
    sql_combined = load_sql("sw_first_term_grades_and_ectp", "4term_cp")
    sql_grades = load_sql("sw_first_term_grades", "4term_cp")

    db = testutil.get_db_connection()

    df = read_sql_query(sql_grades, db)
    grade_only = df[["DurchschnittsnoteBestanden", "DurchschnittsnoteTotal"]]

    df = read_sql_query(sql_combined, db)
    combined = df[["DurchschnittsnoteBestanden", "DurchschnittsnoteTotal"]]

    assert grade_only.equals(combined)


def test_listing_available_features():

    expected = ['cs_first_term_ects',
                'cs_first_term_grades',
                'cs_first_term_grades_and_ectp',
                'cs_first_term_modules',
                'sw_first_term_ects',
                'sw_first_term_grades',
                'sw_first_term_grades_and_ectp',
                'sw_second_term_base_modules'
                ]
    actual = list_available_features()

    assert expected == actual


def test_listing_available_labels():

    expected = ['3_dropout',
                '4term_ap',
                '4term_cp',
                'master_admission',
                'reg_final_grade',
                'reg_study_duration',
                'rsz',
                'study_duration',
                ]
    actual = list_available_labels()

    assert expected == actual
