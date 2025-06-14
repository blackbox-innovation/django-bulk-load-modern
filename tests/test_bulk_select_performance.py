"""
Performance tests for bulk_select_model_dicts with large datasets.
"""
import time
from django.test import TestCase
from django_bulk_load import bulk_select_model_dicts
from .test_project.models import TestComplexModel, TestForeignKeyModel


class TestBulkSelectPerformance(TestCase):
    """Performance tests for bulk_select_model_dicts."""
    
    def setUp(self):
        """Create a foreign key for test data."""
        self.foreign = TestForeignKeyModel()
        self.foreign.save()
    
    def test_performance_100_rows(self):
        """Test performance with 100 rows."""
        self._test_performance(100)
    
    def test_performance_1000_rows(self):
        """Test performance with 1000 rows."""
        self._test_performance(1000)
    
    def test_performance_large_filter_data(self):
        """Test performance with large filter data sets."""
        # Create 100 models
        models = []
        for i in range(100):
            model = TestComplexModel(
                integer_field=i,
                string_field=f"test_{i}",
                json_field={"id": i},
                test_foreign=self.foreign
            )
            models.append(model)
        TestComplexModel.objects.bulk_create(models)
        
        # Prepare filter data for all 100 models
        filter_data = [(i,) for i in range(100)]
        
        # Measure selection time
        start_time = time.time()
        results = bulk_select_model_dicts(
            model_class=TestComplexModel,
            filter_field_names=["integer_field"],
            filter_data=filter_data,
            select_field_names=["integer_field", "string_field"],
        )
        end_time = time.time()
        
        # Verify results
        self.assertEqual(len(results), 100)
        
        # Performance assertion - should complete in reasonable time
        execution_time = end_time - start_time
        self.assertLess(execution_time, 1.0, 
                       f"Query took {execution_time:.3f}s, expected < 1s")
    
    def test_multi_column_filter_performance(self):
        """Test performance with multi-column filters."""
        # Create test data
        models = []
        for i in range(500):
            model = TestComplexModel(
                integer_field=i,  # Unique integer for each model
                string_field=f"group_{i % 10}",  # 50 models per group
                json_field={"batch": i // 100},
                test_foreign=self.foreign
            )
            models.append(model)
        TestComplexModel.objects.bulk_create(models)
        
        # Multi-column filter data - select specific combinations
        filter_data = [
            (i * 10, f"group_{(i * 10) % 10}")  # Every 10th model
            for i in range(50)
        ]
        
        start_time = time.time()
        results = bulk_select_model_dicts(
            model_class=TestComplexModel,
            filter_field_names=["integer_field", "string_field"],
            filter_data=filter_data,
            select_field_names=["integer_field", "string_field", "json_field"],
        )
        end_time = time.time()
        
        # Should find 50 results (one for each filter combination)
        self.assertEqual(len(results), 50)
        
        execution_time = end_time - start_time
        self.assertLess(execution_time, 1.0,
                       f"Multi-column query took {execution_time:.3f}s")
    
    def test_maximum_parameters(self):
        """Test with maximum number of parameters (near PostgreSQL limit)."""
        # PostgreSQL has a limit of ~32767 parameters
        # Test with a safe number below that
        max_rows = 5000  # 5000 rows * 2 fields = 10000 parameters
        
        models = []
        for i in range(max_rows):
            model = TestComplexModel(
                integer_field=i,
                string_field=f"max_test_{i}",
                test_foreign=self.foreign
            )
            models.append(model)
        
        # Bulk create in batches to avoid memory issues
        batch_size = 1000
        for i in range(0, len(models), batch_size):
            TestComplexModel.objects.bulk_create(models[i:i+batch_size])
        
        # Prepare filter data for half the models
        filter_data = [(i, f"max_test_{i}") for i in range(0, max_rows, 2)]
        
        start_time = time.time()
        results = bulk_select_model_dicts(
            model_class=TestComplexModel,
            filter_field_names=["integer_field", "string_field"],
            filter_data=filter_data,
            select_field_names=["integer_field"],
        )
        end_time = time.time()
        
        self.assertEqual(len(results), len(filter_data))
        
        execution_time = end_time - start_time
        # Allow more time for large parameter sets
        self.assertLess(execution_time, 5.0,
                       f"Large parameter query took {execution_time:.3f}s")
    
    def _test_performance(self, num_rows):
        """Helper method to test performance with a given number of rows."""
        # Create test data
        models = []
        for i in range(num_rows):
            model = TestComplexModel(
                integer_field=i,
                string_field=f"perf_test_{i}",
                json_field={"index": i, "data": f"value_{i}"},
                test_foreign=self.foreign
            )
            models.append(model)
        
        # Bulk create for efficiency
        TestComplexModel.objects.bulk_create(models)
        
        # Prepare filter data for half the models
        filter_data = [(i,) for i in range(0, num_rows, 2)]
        
        # Measure query time
        start_time = time.time()
        results = bulk_select_model_dicts(
            model_class=TestComplexModel,
            filter_field_names=["integer_field"],
            filter_data=filter_data,
            select_field_names=["integer_field", "string_field", "json_field"],
        )
        end_time = time.time()
        
        # Verify results
        self.assertEqual(len(results), len(filter_data))
        
        # Log performance
        execution_time = end_time - start_time
        print(f"\nPerformance test with {num_rows} rows: {execution_time:.3f}s")
        print(f"Filtered {len(filter_data)} rows")
        print(f"Average time per row: {execution_time/len(filter_data)*1000:.2f}ms")
        
        # Performance assertions
        if num_rows <= 100:
            self.assertLess(execution_time, 0.5)
        elif num_rows <= 1000:
            self.assertLess(execution_time, 2.0)
        else:
            self.assertLess(execution_time, 10.0)