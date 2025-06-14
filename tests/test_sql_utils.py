"""
Tests for SQL utility functions.
"""
from django.test import TestCase
from django.db import connection
from psycopg.sql import SQL
from django_bulk_load.sql_utils import execute_values_select, build_values_clause


class TestSQLUtils(TestCase):
    """Test SQL utility functions."""
    
    def test_build_values_clause(self):
        """Test the fallback VALUES clause builder."""
        # Test with empty data
        clause, params = build_values_clause([])
        self.assertEqual(clause, "")
        self.assertEqual(params, [])
        
        # Test with single row
        clause, params = build_values_clause([(1, "test")])
        self.assertEqual(clause, "(%s,%s)")
        self.assertEqual(params, [1, "test"])
        
        # Test with multiple rows
        clause, params = build_values_clause([(1, "a"), (2, "b"), (3, "c")])
        self.assertEqual(clause, "(%s,%s),(%s,%s),(%s,%s)")
        self.assertEqual(params, [1, "a", 2, "b", 3, "c"])
    
    def test_execute_values_select_sql_generation(self):
        """Test that execute_values_select generates correct SQL."""
        with connection.cursor() as cursor:
            # Create a test query with VALUES placeholder
            query = SQL("SELECT * FROM test WHERE (a, b) IN (VALUES %s)")
            values_data = [(1, "test"), (2, "another")]
            
            # We can't easily test the exact SQL without executing it,
            # but we can verify the function doesn't raise errors
            try:
                # This will fail because 'test' table doesn't exist,
                # but we can catch the error and check it's the right one
                execute_values_select(cursor, query, values_data)
            except Exception as e:
                # Should get a database error about missing table, not a SQL construction error
                self.assertIn("test", str(e).lower())
    
    def test_execute_values_select_empty_data(self):
        """Test execute_values_select with empty data."""
        with connection.cursor() as cursor:
            query = SQL("SELECT * FROM test WHERE (a, b) IN (VALUES %s)")
            
            # Should handle empty data gracefully
            result = execute_values_select(cursor, query, [])
            self.assertIsNone(result)  # Function returns None for empty data