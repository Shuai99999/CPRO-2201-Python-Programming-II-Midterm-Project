
class Reports:
    def available_equipment(self, con):
        cur = con.execute(
            """
            SELECT
                e.equipment_id,
                e.name,
                e.category,
                e.total_quantity,
                e.total_quantity -
                    COALESCE(SUM(l.loan_quantity), 0) AS available
            FROM equipment e
            LEFT JOIN loans l
                ON e.equipment_id = l.equipment_id
                AND l.return_date IS NULL
            GROUP BY
                e.equipment_id,
                e.name,
                e.category,
                e.total_quantity
            HAVING available > 0
            """
        )

        rows = cur.fetchall()

        if rows:
            for row in rows:
                print(
                    row["equipment_id"],
                    row["name"],
                    row["category"],
                    "Available:", row["available"]
                )
        else:
            print("No equipment available")


    def outstanding_loans(self, con):
        cur = con.execute(
            """
            SELECT
                l.loan_id,
                m.name AS member_name,
                e.name AS equipment_name,
                l.loan_quantity,
                l.loan_date
            FROM loans l
            JOIN member m ON l.member_id = m.id
            JOIN equipment e ON l.equipment_id = e.equipment_id
            WHERE l.return_date IS NULL
            ORDER BY l.loan_id
            """
        )

        rows = cur.fetchall()

        if rows:
            for row in rows:
                print(
                    row["loan_id"],
                    row["member_name"],
                    row["equipment_name"],
                    row["loan_quantity"],
                    row["loan_date"]
                )
        else:
            print("No outstanding loans found")


    def summary_statistics(self, con):
        cur = con.execute(
            "SELECT COALESCE(SUM(total_quantity), 0) AS total FROM equipment"
        )
        total_equipment = cur.fetchone()["total"]

        cur = con.execute(
            "SELECT COUNT(*) AS total FROM member"
        )
        total_members = cur.fetchone()["total"]

        cur = con.execute(
            """SELECT COUNT(*) AS total
               FROM loans
               WHERE return_date IS NULL"""
        )
        outstanding_loans = cur.fetchone()["total"]

        print("===== Summary Statistics =====")
        print("Total Equipment:", total_equipment)
        print("Registered Members:", total_members)
        print("Outstanding Loans:", outstanding_loans)
