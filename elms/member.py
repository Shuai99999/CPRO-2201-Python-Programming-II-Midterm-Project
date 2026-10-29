class Member:
    def __init__(self, name, contact):
        self.id = None
        self.name = name
        self.contact = contact

    def add_member(self, con):
        cur = con.execute(
            "INSERT INTO MEMBER(name, contact) VALUES(?, ?)", (self.name, self.contact)
        )
        self.id = cur.lastrowid
        con.commit()

    def query_member_by_id(self, con, id):
        cur = con.execute("SELECT id, name, contact FROM MEMBER WHERE id = ?", (id,))
        row = cur.fetchone()
        if row is not None:
            print(row["id"], row["name"], row["contact"])
        else:
            print("Member not found")


    def display_all_members(self, con):
        rows = con.execute("SELECT id, name, contact FROM member ORDER BY id").fetchall()
        if not rows:
            print("No members found")
        for row in rows:
            print(row["id"], row["name"], row["contact"])

    def update_member(self, con, member_id, name, contact):
        if member_id <= 0 or not name.strip() or not contact.strip():
            print("A positive member ID, name and contact are required")
            return
        with con:
            cur = con.execute(
                "UPDATE member SET name = ?, contact = ? WHERE id = ?",
                (name.strip(), contact.strip(), member_id)
            )
        print("Member updated successfully" if cur.rowcount else "Member not found")
