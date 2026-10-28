from elms.database import get_connection, initialize_database
from elms.member import Member

initialize_database()
con = get_connection()

m1 = Member("Shuai", "gaoshuai099@gmail.com")
# m1.add_member(con)
m1.query_member_by_id(con, 1)

con.close()
