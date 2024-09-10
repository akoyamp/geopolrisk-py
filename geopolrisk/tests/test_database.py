import unittest
import os
import sqlite3
from geopolrisk.assessment.database import execute_query, database

# execute this test from the root-folde by "python -m unittest geopolrisk/tests/test_database.py"

class TestDatabaseModule(unittest.TestCase):

    # Initialize the database class
    db_instance = database()

    @classmethod
    def setUpClass(cls):
        # Create a test database for testing
        cls.test_db_path = os.path.join(os.path.dirname(__file__), 'test_database.db')
        cls.connection = sqlite3.connect(cls.test_db_path)
        cls.cursor = cls.connection.cursor()
        cls.setup_test_data()

    @classmethod
    def setup_test_data(cls):
        # Create tables and insert test data
        cls.cursor.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)")
        cls.cursor.execute("INSERT INTO test_table (name) VALUES ('Test1'), ('Test2'), ('Test3')")
        cls.connection.commit()

    @classmethod
    def tearDownClass(cls):
        # Clean up test database
        cls.connection.close()
        os.remove(cls.test_db_path)

    def test_execute_query_select(self):
        # Test SELECT query execution
        query = "SELECT * FROM test_table"
        results = execute_query(query, self.test_db_path)
        self.assertEqual(len(results), 3)  # Adjusted to match the number of inserted rows
        self.assertEqual(results[0][1], 'Test1')

    def test_execute_query_insert(self):
        # Test INSERT query execution
        query = "INSERT INTO test_table (name) VALUES ('Test4')"
        execute_query(query, self.test_db_path)
        results = execute_query("SELECT * FROM test_table", self.test_db_path)
        self.assertEqual(len(results), 4)  # Updated to reflect new total
        self.assertEqual(results[3][1], 'Test4')

    def test_check_db_tables(self):
        # Test checking for existing tables
        self.cursor.execute("CREATE TABLE another_table (id INTEGER PRIMARY KEY)")
        self.connection.commit()
        self.assertTrue(self.db_instance.check_db_tables(self.test_db_path, ['test_table', 'another_table']))
        self.assertFalse(self.db_instance.check_db_tables(self.test_db_path, ['non_existing_table']))

    def test_extract_tables_to_df(self):
        # Test extracting tables to DataFrame
        tables = self.db_instance.extract_tables_to_df(self.test_db_path, self.db_instance.Tables_world_mining_data)
        self.assertIn('Aluminium', tables)

if __name__ == '__main__':
    unittest.main()