
from datetime import date


class Loan:
    def __init__(self, member_id, equipment_id, loan_quantity):
        self.loan_id = None
        self.member_id = member_id
        self.equipment_id = equipment_id
        self.loan_quantity = loan_quantity

    def add_loan(self, con):
        if self.loan_quantity <= 0:
            print("Loan quantity must be greater than zero")
            return

        cur = con.execute(
            "SELECT id FROM member WHERE id = ?",
            (self.member_id,)
        )

        if cur.fetchone() is None:
            print("Member not found")
            return

        cur = con.execute(
            "SELECT total_quantity FROM equipment WHERE equipment_id = ?",
            (self.equipment_id,)
        )

        equipment = cur.fetchone()

        if equipment is None:
            print("Equipment not found")
            return

        cur = con.execute(
            """SELECT COALESCE(SUM(loan_quantity), 0) AS borrowed
               FROM loans
               WHERE equipment_id = ? AND return_date IS NULL""",
            (self.equipment_id,)
        )

        borrowed = cur.fetchone()["borrowed"]
        available = equipment["total_quantity"] - borrowed

        if self.loan_quantity > available:
            print("Insufficient equipment available")
            return

        cur = con.execute(
            """INSERT INTO loans
               (member_id, equipment_id, loan_quantity, loan_date)
               VALUES (?, ?, ?, ?)""",
            (
                self.member_id,
                self.equipment_id,
                self.loan_quantity,
                date.today().isoformat()
            )
        )

        self.loan_id = cur.lastrowid
        con.commit()
        print("Loan recorded successfully")


    def return_loan(self, con, loan_id):
        cur = con.execute(
            "SELECT return_date FROM loans WHERE loan_id = ?",
            (loan_id,)
        )

        loan = cur.fetchone()

        if loan is None:
            print("Loan not found")
            return

        if loan["return_date"] is not None:
            print("Equipment already returned")
            return

        cur = con.execute(
            "UPDATE loans SET return_date = ? WHERE loan_id = ?",
            (date.today().isoformat(), loan_id)
        )

        con.commit()
        print("Equipment returned successfully")


    def display_member_loans(self, con, member_id):
        cur = con.execute(
            """SELECT loan_id, member_id, equipment_id,
                      loan_quantity, loan_date
               FROM loans
               WHERE member_id = ? AND return_date IS NULL""",
            (member_id,)
        )

        rows = cur.fetchall()

        if rows:
            for row in rows:
                print(
                    row["loan_id"],
                    row["member_id"],
                    row["equipment_id"],
                    row["loan_quantity"],
                    row["loan_date"]
                )
        else:
            print("No current loans found for this member")


    def display_outstanding_loans(self, con):
        cur = con.execute(
            """SELECT loan_id, member_id, equipment_id,
                      loan_quantity, loan_date
               FROM loans
               WHERE return_date IS NULL"""
        )

        rows = cur.fetchall()

        if rows:
            for row in rows:
                print(
                    row["loan_id"],
                    row["member_id"],
                    row["equipment_id"],
                    row["loan_quantity"],
                    row["loan_date"]
                )
        else:
            print("No outstanding loans found")
