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
