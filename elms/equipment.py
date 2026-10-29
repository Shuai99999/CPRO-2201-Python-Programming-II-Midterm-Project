
class Equipment:
    def __init__(self, name, category, total_quantity):
        self.equipment_id = None
        self.name = name
        self.category = category
        self.total_quantity = total_quantity

    def add_equipment(self, con):
        if self.total_quantity < 0:
            print("Quantity cannot be negative")
            return

        cur = con.execute(
            """INSERT INTO equipment(name, category, total_quantity)
               VALUES (?, ?, ?)""",
            (self.name, self.category, self.total_quantity)
        )

        self.equipment_id = cur.lastrowid
        con.commit()
        print("Equipment added successfully")

    def display_all_equipment(self, con):
        cur = con.execute(
            "SELECT equipment_id, name, category, total_quantity FROM equipment"
        )

        rows = cur.fetchall()

        if rows:
            for row in rows:
                print(
                    row["equipment_id"],
                    row["name"],
                    row["category"],
                    row["total_quantity"]
                )
        else:
            print("No equipment found")   


    def search_equipment(self, con, keyword):
        cur = con.execute(
            """SELECT equipment_id, name, category, total_quantity
               FROM equipment
               WHERE name LIKE ? OR category LIKE ?""",
            (f"%{keyword}%", f"%{keyword}%")
        )

        rows = cur.fetchall()

        if rows:
            for row in rows:
                print(
                    row["equipment_id"],
                    row["name"],
                    row["category"],
                    row["total_quantity"]
                )
        else:
            print("No matching equipment found")


    def update_equipment(self, con, equipment_id, name, category, total_quantity):
        if total_quantity < 0:
            print("Quantity cannot be negative")
            return

        borrowed = con.execute(
            "SELECT COALESCE(SUM(loan_quantity), 0) FROM loans "
            "WHERE equipment_id = ? AND return_date IS NULL", (equipment_id,)
        ).fetchone()[0]
        if total_quantity < borrowed:
            print(f"Quantity cannot be less than the {borrowed} units currently on loan")
            return

        cur = con.execute(
            """UPDATE equipment
               SET name = ?, category = ?, total_quantity = ?
               WHERE equipment_id = ?""",
            (name, category, total_quantity, equipment_id)
        )

        if cur.rowcount > 0:
            con.commit()
            print("Equipment updated successfully")
        else:
            print("Equipment not found")


    def remove_equipment(self, con, equipment_id):
        if con.execute("SELECT 1 FROM loans WHERE equipment_id = ?", (equipment_id,)).fetchone():
            print("Cannot remove equipment with loan history; its records must be preserved")
            return
        cur = con.execute(
            "DELETE FROM equipment WHERE equipment_id = ?",
            (equipment_id,)
        )

        if cur.rowcount > 0:
            con.commit()
            print("Equipment removed successfully")
        else:
            print("Equipment not found")
