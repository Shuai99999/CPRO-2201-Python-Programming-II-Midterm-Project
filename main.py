import sqlite3


from elms.database import get_connection, initialize_database
from elms.member import Member
from elms.equipment import Equipment
from elms.loan import Loan
from elms.reports import Reports

def get_integer(prompt, minimum=1):
    while True:
        try:
            value = int(input(prompt))
            if value < minimum:
                print(f"Please enter a whole number of at least {minimum}.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a whole number.")

def get_text(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")


def run_menu(con):
    while True:
        print("\n===== Equipment Lending Management System =====")
        print("1. Equipment Management")
        print("2. Member Management")
        print("3. Lending and Returns")
        print("4. Reports")
        print("0. Exit")

        choice = input("Enter your choice: ")

       
        if choice == "1":
            while True:
                print("\n===== Equipment Management =====")
                print("1. Register Equipment")
                print("2. Display All Equipment")
                print("3. Search Equipment")
                print("4. Update Equipment")
                print("5. Remove Equipment")
                print("0. Back to Main Menu")

                equipment_choice = input("Enter your choice: ")

                if equipment_choice == "1":
                   name = get_text("Enter equipment name: ")
                   category = get_text("Enter equipment category: ")
                   quantity = get_integer("Enter total quantity: ", minimum=0)

                   equipment = Equipment(name, category, quantity)
                   equipment.add_equipment(con)

                elif equipment_choice == "2":
                     equipment = Equipment("", "", 0)
                     equipment.display_all_equipment(con)

                elif equipment_choice == "3":
                     keyword = input("Enter equipment name or category: ")

                     equipment = Equipment("", "", 0)
                     equipment.search_equipment(con, keyword)

                elif equipment_choice == "4":
                     equipment_id = get_integer("Enter equipment ID: ")
                     name = get_text("Enter new equipment name: ")
                     category = get_text("Enter new category: ")
                     quantity = get_integer("Enter new total quantity: ", minimum=0)

                     equipment = Equipment("", "", 0)
                     equipment.update_equipment(
                         con, equipment_id, name, category, quantity
                        )

                elif equipment_choice == "5":
                     equipment_id = get_integer("Enter equipment ID to remove: ")

                     equipment = Equipment("", "", 0)
                     equipment.remove_equipment(con, equipment_id)

                elif equipment_choice == "0":
                    break

                else:
                    print("Invalid choice. Please try again.")


        
        elif choice == "2":
            while True:
                print("\n===== Member Management =====")
                print("1. Register Member")
                print("2. Display All Members")
                print("3. Search Member by ID")
                print("4. Update Member")
                print("0. Back to Main Menu")

                member_choice = input("Enter your choice: ")

                if member_choice == "1":
                   name = get_text("Enter member name: ")
                   contact = get_text("Enter member contact: ")

                   member = Member(name, contact)
                   member.add_member(con)

                   print("Member registered successfully")

                elif member_choice == "2":
                     member = Member("", "")
                     member.display_all_members(con)

                elif member_choice == "3":
                     member_id = get_integer("Enter member ID: ")

                     member = Member("", "")
                     member.query_member_by_id(con, member_id)

                elif member_choice == "4":
                     member_id = get_integer("Enter member ID: ")
                     name = get_text("Enter new member name: ")
                     contact = get_text("Enter new member contact: ")

                     member = Member("", "")
                     member.update_member(con, member_id, name, contact)

                elif member_choice == "0":
                    break

                else:
                    print("Invalid choice. Please try again.")


       
        elif choice == "3":
            while True:
                print("\n===== Lending and Returns =====")
                print("1. Record Equipment Loan")
                print("2. Return Equipment")
                print("3. Display Member's Current Loans")
                print("4. Display All Outstanding Loans")
                print("0. Back to Main Menu")

                loan_choice = input("Enter your choice: ")

                if loan_choice == "1":
                    member_id = get_integer("Enter member ID: ")
                    equipment_id = get_integer("Enter equipment ID: ")
                    quantity = get_integer("Enter loan quantity: ")

                    loan = Loan(member_id, equipment_id, quantity)
                    loan.add_loan(con)

                elif loan_choice == "2":
                    loan_id = get_integer("Enter loan ID to return: ")

                    loan = Loan(0, 0, 0)
                    loan.return_loan(con, loan_id)

                elif loan_choice == "3":
                    member_id = get_integer("Enter member ID: ")

                    loan = Loan(0, 0, 0)
                    loan.display_member_loans(con, member_id)

                elif loan_choice == "4":
                    loan = Loan(0, 0, 0)
                    loan.display_outstanding_loans(con)

                elif loan_choice == "0":
                    break

                else:
                    print("Invalid choice. Please try again.")


        
        elif choice == "4":
            report = Reports()

            while True:
                print("\n===== Reports =====")
                print("1. Available Equipment")
                print("2. Outstanding Loans")
                print("3. Summary Statistics")
                print("0. Back to Main Menu")

                report_choice = input("Enter your choice: ")

                if report_choice == "1":
                    report.available_equipment(con)

                elif report_choice == "2":
                    report.outstanding_loans(con)

                elif report_choice == "3":
                    report.summary_statistics(con)

                elif report_choice == "0":
                    break

                else:
                    print("Invalid choice. Please try again.")


        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

def main():
    """Keep resources closed even when input ends or a database action fails."""
    con = None
    try:
        initialize_database()
        con = get_connection()
        while True:
            try:
                run_menu(con)
                break
            except sqlite3.IntegrityError:
                con.rollback()
                print("The change conflicts with existing records. No change was saved.")
            except sqlite3.Error as error:
                con.rollback()
                print(f"Database operation failed: {error}. Returning to the main menu.")
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
    except sqlite3.Error as error:
        print(f"Unable to open or initialize the database: {error}")
    finally:
        if con is not None:
            con.close()


if __name__ == "__main__":
    main()
