import sqlite3


def get_connection():
    con = sqlite3.connect("elms.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con


def initialize_database():
    con = get_connection()

    sql = """
  CREATE TABLE IF NOT EXISTS equipment(
    equipment_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    total_quantity INTEGER NOT NULL CHECK(total_quantity >= 0)
  )
  """

    con.execute(sql)

    sql = """
  CREATE TABLE IF NOT EXISTS member(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    contact TEXT NOT NULL
  )
  """

    con.execute(sql)

    sql = """
  CREATE TABLE IF NOT EXISTS loans(
    loan_id INTEGER PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES member(id),
    equipment_id INTEGER NOT NULL REFERENCES equipment(equipment_id),
    loan_quantity INTEGER NOT NULL CHECK(loan_quantity > 0),
    loan_date TEXT NOT NULL,
    return_date TEXT
  )
  """

    con.execute(sql)

    con.commit()
    con.close()
