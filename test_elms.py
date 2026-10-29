import contextlib
import io
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import main
from elms import database
from elms.equipment import Equipment
from elms.loan import Loan
from elms.member import Member
from elms.reports import Reports

class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path_patch = patch.object(database, 'DATABASE_PATH', Path(self.temp.name)/'test.db')
        self.path_patch.start()
        database.initialize_database()
        self.con = database.get_connection()
        self.output = io.StringIO()
        self.capture = contextlib.redirect_stdout(self.output)
        self.capture.__enter__()
        Member('Festus', 'festus@example.test').add_member(self.con)
        Equipment('Camera', 'Media', 3).add_equipment(self.con)

    def tearDown(self):
        self.capture.__exit__(None, None, None)
        self.con.close()
        self.path_patch.stop()
        self.temp.cleanup()

    def test_loan_return_and_availability(self):
        loan = Loan(1,1,2)
        loan.add_loan(self.con)
        Reports().available_equipment(self.con)
        self.assertIn('Available: 1', self.output.getvalue())
        Loan(1,1,2).add_loan(self.con)
        self.assertEqual(self.con.execute('SELECT COUNT(*) FROM loans').fetchone()[0], 1)
        loan.return_loan(self.con, loan.loan_id)
        loan.return_loan(self.con, loan.loan_id)
        self.assertIn('already returned', self.output.getvalue())
        Reports().available_equipment(self.con)
        self.assertIn('Available: 3', self.output.getvalue())

    def test_missing_records_and_invalid_quantities(self):
        for args in [(99,1,1),(1,99,1),(1,1,0),(1,1,-1),(0,1,1)]:
            Loan(*args).add_loan(self.con)
        Loan(0,0,0).return_loan(self.con,99)
        Loan(0,0,0).display_member_loans(self.con,99)
        self.assertEqual(self.con.execute('SELECT COUNT(*) FROM loans').fetchone()[0],0)
        self.assertIn('Loan not found',self.output.getvalue())

    def test_stock_update_and_delete_preserve_loans(self):
        Loan(1,1,2).add_loan(self.con)
        equipment=Equipment('', '', 0)
        equipment.update_equipment(self.con,1,'Camera','Media',1)
        equipment.remove_equipment(self.con,1)
        self.assertEqual(self.con.execute('SELECT total_quantity FROM equipment').fetchone()[0],3)
        self.assertIn('loan history',self.output.getvalue())

    def test_members_and_reports(self):
        member=Member('', '')
        member.display_all_members(self.con)
        member.update_member(self.con,1,'Festus Updated','new@example.test')
        member.query_member_by_id(self.con,1)
        Loan(1,1,1).add_loan(self.con)
        Loan(0,0,0).display_member_loans(self.con,1)
        Loan(0,0,0).display_outstanding_loans(self.con)
        Reports().outstanding_loans(self.con)
        Reports().summary_statistics(self.con)
        self.assertIn('Festus Updated Camera',self.output.getvalue())
        self.assertIn('Outstanding Loans: 1',self.output.getvalue())

    def test_integer_and_text_validation(self):
        with patch('builtins.input',side_effect=['abc','0','-1','2']):
            self.assertEqual(main.get_integer('ID: '),2)
        with patch('builtins.input',side_effect=['-1','0']):
            self.assertEqual(main.get_integer('Quantity: ',0),0)
        with patch('builtins.input',side_effect=['  ',' Camera ']):
            self.assertEqual(main.get_text('Name: '),'Camera')

    def test_complete_menu(self):
        answers=['x','1','2','3','Camera','0','2','2','3','1','4','1','Festus','contact','0',
                 '3','1','1','1','1','3','1','4','2','1','0','4','1','2','3','0','0']
        with patch('builtins.input',side_effect=answers):
            main.run_menu(self.con)
        self.assertIn('Equipment returned successfully',self.output.getvalue())
        self.assertIn('Goodbye!',self.output.getvalue())

    def test_persistence_and_foreign_keys(self):
        Loan(1,1,1).add_loan(self.con)
        with contextlib.closing(database.get_connection()) as second:
            self.assertEqual(second.execute('SELECT COUNT(*) FROM loans').fetchone()[0],1)
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute("INSERT INTO loans(member_id,equipment_id,loan_quantity,loan_date) VALUES(99,1,1,'2026-01-01')")
        self.con.rollback()

    def test_empty_reports(self):
        self.con.execute('DELETE FROM member')
        self.con.execute('DELETE FROM equipment')
        self.con.commit()
        Reports().available_equipment(self.con)
        Reports().outstanding_loans(self.con)
        Reports().summary_statistics(self.con)
        self.assertIn('Total Equipment: 0',self.output.getvalue())

if __name__=='__main__':
    unittest.main(verbosity=2)

