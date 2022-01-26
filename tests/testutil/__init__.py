"""
Collection of helper functions for testing purposes.
"""

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
    hauptfach="Informatik",
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


""
