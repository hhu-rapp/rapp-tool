"""
Collection of helper functions for testing purposes.
"""

import pandas as pd
import sqlite3

import tests.resources as rc


def get_empty_memory_db_connection():
    """
    Set up empty rapp database in memory.
    """
    db = sqlite3.connect(":memory:")

    # Create tables
    einschreibung = "CREATE TABLE Einschreibung (ID INTEGER PRIMARY KEY AUTOINCREMENT, Abschluss VARCHAR(30) NOT NULL, Studienfach VARCHAR(50) NOT NULL, Immatrikulationsdatum VARCHAR(10) NOT NULL, Exmatrikulationsdatum VARCHAR(10), Immatrikulationsfach INTEGER NOT NULL, Exmatrikulationsfach INTEGER, Hauptfach BOOLEAN NOT NULL, Bestanden BOOLEAN NOT NULL, Fachwechsler BOOLEAN NOT NULL, Pseudonym INTEGER NOT NULL, CONSTRAINT fk_Pseudonym FOREIGN KEY (Pseudonym) REFERENCES Student(Pseudonym))"
    pruefung = "CREATE TABLE Pruefung (Version INTEGER, Nummer INTEGER, Modul VARCHAR(255) NOT NULL, PRIMARY KEY (Version, Nummer))"
    student = "CREATE TABLE Student (Pseudonym INTEGER PRIMARY KEY, Geburtsjahr INTEGER NOT NULL, Geschlecht INTEGER, Deutsch BOOLEAN)"
    ssp = "CREATE TABLE Student_schreibt_Pruefung (Pseudonym INTEGER, Version INTEGER, Nummer INTEGER, Status VARCHAR(30), Studienfach VARCHAR(50), Abschluss VARCHAR (30), Versuch INTEGER NOT NULL, Note REAL, ECTS INTEGER, Fachsemester INTEGER NOT NULL, Hochschulsemester INTEGER NOT NULL, Anerkennung VARCHAR(100) NOT NULL, Semesterjahr INTEGER NOT NULL, Sommersemester BOOLEAN NOT NULL, HZB VARCHAR(50), Studienform VARCHAR(30), CONSTRAINT fk_Student FOREIGN KEY (Pseudonym) REFERENCES Student(Pseudonym), CONSTRAINT fk_Pruefung FOREIGN KEY (Version) REFERENCES Pruefung(Version), FOREIGN KEY (Nummer) REFERENCES Pruefung(Nummer))"

    cur = db.cursor()
    cur.execute(einschreibung)
    cur.execute(pruefung)
    cur.execute(student)
    cur.execute(ssp)

    return db


def get_db_connection():
    """
    Returns: Connection to a memory database which contains the
    entries of `test.db`.

    Altering the values in the returned connection has no effect onto the
    data of the test.db.
    """
    path = rc.get_path('test.db')
    # Open test db, then copy/backup contents to memory db.
    test_db = sqlite3.connect(path)
    mem_db = sqlite3.connect(":memory:")
    test_db.backup(mem_db)
    return mem_db


def __execute_sql(connection, sql, *args):
    cur = connection.cursor()
    cur.execute(sql, args)
    return cur.lastrowid


def insert_into_Einschreibung(
    conn,
    pseudonym,
    abschluss="Bachelor",
    studienfach="Informatik",
    immatrikulationsdatum="2016-10-01",
    exmatrikulationsdatum="",
    immatrikulationsfach="1234",
    exmatrikulationsfach="",
    hauptfach="Ja",
    bestanden="Nein",
    fachwechsler="Nein",
):
    """
    Insert a new student into the Einschreibung SQL table.
    All fields besides the pseudonym have a default value.
    """
    sql = """
    INSERT INTO Einschreibung(
        Pseudonym,
        Abschluss,
        Studienfach,
        Immatrikulationsdatum,
        Exmatrikulationsdatum,
        Immatrikulationsfach,
        Exmatrikulationsfach,
        Hauptfach,
        Bestanden,
        Fachwechsler
    ) VALUES (?,?,?,?,?,?,?,?,?,?)
    """
    return __execute_sql(conn, sql,
                         pseudonym, abschluss, studienfach,
                         immatrikulationsdatum, exmatrikulationsdatum,
                         immatrikulationsfach, exmatrikulationsfach,
                         hauptfach, bestanden, fachwechsler
                         )


def insert_into_Pruefung(conn, modul, version, nummer):
    sql = "INSERT INTO Pruefung(Version, Nummer, Modul) VALUES(?,?,?)"
    return __execute_sql(conn, sql, version, nummer, modul)


def insert_into_Student(
    conn,
    pseudonym,
    geburtsjahr="1995",
    geschlecht="männlich",
    deutsch="1"
):
    sql = """INSERT INTO Student(Pseudonym, Geburtsjahr, Geschlecht, Deutsch)
          VALUES(?,?,?,?)"""
    return __execute_sql(conn, sql, pseudonym, geburtsjahr, geschlecht, deutsch)


def insert_into_Student_schreibt_Pruefung(
    conn,
    pseudonym,
    version,
    nummer,
    status,
    note,
    ects,
    fachsemester,
    studienfach="Informatik",
    abschluss="Bachelor",
    versuch=1,
    hochschulsemester=None,
    anerkennung="reguläre Leistung",
    semesterjahr="2017",
    sommersemester="1",
    hzb="(Fach) Hochschulreife",
    studienform="Erststudium"
):
    """
    Insert a new exam into the database.
    Most of the columns have a default value.
    If `hochschulsemester` is None, it is set to be equal to `fachsemester`.

    Entries for the pseudonym, the module version and number, the grade,
    `fachsemester`, and resulting grade have always to be specified.
    """
    sql = """
    INSERT INTO Student_schreibt_Pruefung(
        Pseudonym, Version, Nummer,
        Status, Studienfach, Abschluss,
        Versuch, Note, ECTS,
        Fachsemester, Hochschulsemester,
        Anerkennung, Semesterjahr, Sommersemester, HZB, Studienform
    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """

    if hochschulsemester is None:
        hochschulsemester = fachsemester

    return __execute_sql(conn, sql,
                         pseudonym, version, nummer,
                         status, studienfach, abschluss,
                         versuch, note, ects,
                         fachsemester, hochschulsemester,
                         anerkennung, semesterjahr, sommersemester,
                         hzb, studienform
                         )


class TestDb():
    def __init__(self, modules=[], empty=False) -> None:
        if empty:
            self.db = get_empty_memory_db_connection()
        else:
            self.db = get_db_connection()

        self.modules = {}  # Keep versions and numbers under module name as key
        if len(modules) > 0:
            self.add_modules(modules)

        # Keep track of a student's subject
        #   pseudonym -> {"abschluss": str, "studienfach": str}
        self.students = {}


    def add_modules(self, *args):
        """
        Expects a list of tuples `(name, version, number)`.
        For adding a single module, prefer using `add_module` instead.
        """
        for config in args:
            self.add_module(*config)

    def add_module(self, name, version, number):
        insert_into_Pruefung(self.db, name, version, number)
        self.modules[name] = {"version": version, "nummer": number}

    def add_ifo_student(self, pseudonym, **kwargs):
        """
        Adds a new student into the database. Use the following keywords to
        alter the entry as needed. Left-out entries are automatically filled
        by default values.

        See TestDb.add_student for an overview of the parameters.
        """
        return self.add_student(pseudonym, subject="Informatik", **kwargs)

    def add_sw_student(self, pseudonym, **kwargs):
        """
        Adds a new student into the database. Use the following keywords to
        alter the entry as needed. Left-out entries are automatically filled
        by default values.

        See TestDb.add_student for an overview of the parameters.
        """
        return self.add_student(pseudonym, subject="Sozialwiss.- Medien, Pol.", **kwargs)

    def add_student(self, pseudonym, subject, **kwargs):
        """
        Adds a new student into the database. Use the following keywords to
        alter the entry as needed. Left-out entries are automatically filled
        by default values.

        Parameters
        ----------
        pseudonym:
            Pseudonym of the student in the database.
        subject:
            The topic the student studies.
        geburtsjahr:
            Year of birth.
        geschlecht: "männlich", "weiblich", "divers"
            Gender.
        deutsch: 0 or 1
            Whether the student is German (1) or foreign (0)
        immatrikulationsdatum: string, YYYY-MM-DD
            Date of enrolment.
        exmatrikulationsdatum: string, YYYY-MM-DD
            Date of de-registration.
        immatrikulationsfach: int
            Identifier for elected subject on enrolment
        exmatrikulationsfach: int
            Identifier for elected subject on de-registration
        bestanden: 0 or 1
            Whether the degree was finished or not.
        fachwechsler:
            Whether the subject was changed from original enrolment subject or not.
        """

        student_fields = ["geburtsjahr", "geschlecht", "deutsch"]
        enrolment_fields = [
            # "abschluss", "studienfach",
            "immatrikulationsdatum", "exmatrikulationsdatum",
            "exmatrikulationsfach",
            # "hauptfach",
            "bestanden", "fachwechsler"
        ]

        student = {key: kwargs[key] for key in student_fields if key in kwargs}

        enrol = {key: kwargs[key] for key in enrolment_fields if key in kwargs}
        enrol["studienfach"] = subject

        insert_into_Student(self.db, pseudonym, **student)
        insert_into_Einschreibung(self.db, pseudonym, **enrol)

        self.students[pseudonym] = {
            "abschluss": enrol.get("Abschluss", "Bachelor"),
            "studienfach": subject
        }

        return pseudonym

    def add_exam(self, pseudonym, module, attempt, semester,
                 passed=False, ects=0, grade=5.0, **kwargs):
        """
        Adds an exam result to the database for the given student.

        Parameters:
        -----------
        pseudonym: int
            Pseudonym of a student in the database.
        module: str
            Name of a module in the database.
        attempt: int
            Attempt number.
        semester: int
            Semester of the student in which they wrote this exam.
        passed: bool
            Whether the exam was passed.
        ects: float
            Number of ECTP earned.
        grade: float
            Assigned grade.

        version: int
            Version number of the exam.
        nummer: int
            ID of the exam.
        status: "bestanden", "nicht bestanden", "endgültig nicht bestanden"
            Overrides `passed`.
        studienfach: str
            Degree subject in which the exam was written.
        abschluss:
            Degree level for which the exam was written
        hochschulsemester: int
        anerkennung: str
        semesterjahr: int
            Year of the exam
        sommersemester: bool
            Whether it was summer or winter term
        hzb: str
        studienform: str

        status:
        note,
        ects,
        fachsemester,
        versuch=1,
        """
        # Create base for entry.
        ssp = {
            "pseudonym": pseudonym,
            "status": "bestanden" if passed else "nicht bestanden",
            "note": grade,
            "ects": ects,
            "fachsemester": semester,
            "versuch": attempt,
            # Student info
            "studienfach": self.students[pseudonym]["studienfach"],
            "abschluss": self.students[pseudonym]["abschluss"],
            # Exam info
            "nummer": self.modules[module].get("nummer"),
            "version": self.modules[module].get("version"),
        }

        # Update with more detailed information.
        for key in kwargs:
            ssp[key] = kwargs[key]

        insert_into_Student_schreibt_Pruefung(self.db, **ssp)

    def read_sql_query(self, sql_query):
        return pd.read_sql_query(sql_query, self.db)
