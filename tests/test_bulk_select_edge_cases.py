"""
Edge case tests for bulk_select_model_dicts with psycopg3 SQL composition.
"""
from datetime import datetime, timezone
from django.test import TestCase
from django_bulk_load import bulk_select_model_dicts
from .test_project.models import TestComplexModel, TestForeignKeyModel


class TestBulkSelectEdgeCases(TestCase):
    """Test edge cases and security concerns for bulk_select_model_dicts."""
    
    def setUp(self):
        """Create some test data."""
        self.foreign = TestForeignKeyModel()
        self.foreign.save()
        
    def test_sql_injection_attempts(self):
        """Test that SQL injection attempts are properly escaped."""
        # Create models with potentially dangerous values
        dangerous_values = [
            "'; DROP TABLE test_project_testcomplexmodel; --",
            "1' OR '1'='1",
            "1); DELETE FROM test_project_testcomplexmodel; --",
            "Robert'); DROP TABLE Students;--",
        ]
        
        models = []
        for i, danger in enumerate(dangerous_values):
            model = TestComplexModel(
                integer_field=i,
                string_field=danger,
                json_field={"danger": danger},
                test_foreign=self.foreign
            )
            model.save()
            models.append(model)
        
        # Try to select using the dangerous values
        for i, danger in enumerate(dangerous_values):
            results = bulk_select_model_dicts(
                model_class=TestComplexModel,
                filter_field_names=["string_field"],
                filter_data=[(danger,)],
                select_field_names=["integer_field", "string_field"],
            )
            
            # Should find exactly one result with matching data
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["string_field"], danger)
            self.assertEqual(results[0]["integer_field"], i)
    
    def test_special_characters(self):
        """Test handling of special characters in values."""
        special_chars = [
            "test with 'single quotes'",
            'test with "double quotes"',
            "test with `backticks`",
            "test with \\backslash",
            "test with \n newline",
            "test with \t tab",
            "test with NULL",
            "test with %s placeholder",
            "test with $1 dollar placeholder",
        ]
        
        models = []
        for i, special in enumerate(special_chars):
            model = TestComplexModel(
                integer_field=i,
                string_field=special,
                test_foreign=self.foreign
            )
            model.save()
            models.append(model)
        
        # Select using special characters
        for i, special in enumerate(special_chars):
            results = bulk_select_model_dicts(
                model_class=TestComplexModel,
                filter_field_names=["string_field"],
                filter_data=[(special,)],
                select_field_names=["integer_field", "string_field"],
            )
            
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["string_field"], special)
    
    def test_null_values(self):
        """Test filtering and selecting NULL values.
        
        Note: SQL IN clauses don't match NULL values because NULL != NULL in SQL.
        This is a known limitation of using (col) IN (VALUES ...) syntax.
        """
        # Create models with various NULL combinations
        models = [
            TestComplexModel(integer_field=1, string_field=None, json_field=None),
            TestComplexModel(integer_field=2, string_field="not null", json_field=None),
            TestComplexModel(integer_field=None, string_field="null int", json_field={"a": 1}),
            TestComplexModel(integer_field=None, string_field=None, json_field=None),
        ]
        for model in models:
            model.save()
        
        # Test filtering by NULL values - this won't work with IN clause
        # NULL values in SQL require IS NULL, not = NULL or IN (NULL)
        results = bulk_select_model_dicts(
            model_class=TestComplexModel,
            filter_field_names=["string_field"],
            filter_data=[(None,)],
            select_field_names=["integer_field", "string_field", "json_field"],
        )
        
        # SQL IN clause doesn't match NULL values
        self.assertEqual(len(results), 0)
        
        # Test with non-NULL values works correctly
        results = bulk_select_model_dicts(
            model_class=TestComplexModel,
            filter_field_names=["string_field"],
            filter_data=[("not null",), ("null int",)],
            select_field_names=["integer_field", "string_field", "json_field"],
        )
        
        self.assertEqual(len(results), 2)
        string_values = {r["string_field"] for r in results}
        self.assertEqual(string_values, {"not null", "null int"})
    
    def test_empty_strings(self):
        """Test handling of empty strings vs NULL."""
        models = [
            TestComplexModel(integer_field=1, string_field=""),
            TestComplexModel(integer_field=2, string_field=None),
            TestComplexModel(integer_field=3, string_field=" "),  # space
        ]
        for model in models:
            model.save()
        
        # Filter by empty string
        results = bulk_select_model_dicts(
            model_class=TestComplexModel,
            filter_field_names=["string_field"],
            filter_data=[("",)],
            select_field_names=["integer_field", "string_field"],
        )
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["string_field"], "")
        self.assertEqual(results[0]["integer_field"], 1)
    
    def test_unicode_and_emoji(self):
        """Test Unicode and emoji handling."""
        unicode_values = [
            "Hello 世界",
            "Привет мир",
            "مرحبا بالعالم",
            "🐍 Python 🚀",
            "Complex: 你好👋 мир 🌍",
        ]
        
        for i, unicode_val in enumerate(unicode_values):
            model = TestComplexModel(
                integer_field=i,
                string_field=unicode_val,
                json_field={"text": unicode_val},
                test_foreign=self.foreign
            )
            model.save()
        
        # Select using Unicode values
        for i, unicode_val in enumerate(unicode_values):
            results = bulk_select_model_dicts(
                model_class=TestComplexModel,
                filter_field_names=["string_field"],
                filter_data=[(unicode_val,)],
                select_field_names=["integer_field", "string_field", "json_field"],
            )
            
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["string_field"], unicode_val)
            self.assertEqual(results[0]["json_field"]["text"], unicode_val)
    
    def test_very_long_strings(self):
        """Test handling of very long strings."""
        long_string = "x" * 10000  # 10k characters
        
        model = TestComplexModel(
            integer_field=1,
            string_field=long_string,
            test_foreign=self.foreign
        )
        model.save()
        
        results = bulk_select_model_dicts(
            model_class=TestComplexModel,
            filter_field_names=["string_field"],
            filter_data=[(long_string,)],
            select_field_names=["integer_field"],
        )
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["integer_field"], 1)