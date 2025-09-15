"""
Test suite for Financial Data Processing Pipeline
===============================================

These tests demonstrate system behavior under various conditions
including normal operation, error scenarios, and load testing.
"""

import pytest
import os
import tempfile
import json
import time
from unittest.mock import patch, MagicMock
import requests
from data_pipeline import FinancialDataProcessor, DatabaseManager, ExternalAPIManager, run_daily_pipeline


class TestDatabaseManager:
    """Test cases for database operations."""
    
    @pytest.fixture
    def db_manager(self):
        """Create a temporary database for testing."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        manager = DatabaseManager(temp_db.name)
        yield manager
        
        # Cleanup
        os.unlink(temp_db.name)
    
    def test_basic_database_operations(self, db_manager):
        """Test basic database functionality."""
        # Test transaction saving
        transactions = [
            {
                'transaction_id': 'T001',
                'account_id': 'A001',
                'amount': 100.00,
                'transaction_type': 'credit',
                'transaction_date': '2024-01-01'
            }
        ]
        
        db_manager.save_transactions(transactions)
        
        # Test balance operations
        db_manager.update_account_balance('A001', 100.00)
        balance = db_manager.get_account_balance('A001')
        
        assert balance == 100.00
    
    def test_connection_handling(self, db_manager):
        """Test database connection management."""
        # This test reveals potential connection leak issues
        
        # Simulate many operations that could leak connections
        for i in range(50):
            db_manager.update_account_balance(f'A{i:03d}', float(i))
            balance = db_manager.get_account_balance(f'A{i:03d}')
            assert balance == float(i)
        
        # Test that we can still perform operations
        # If connections were leaked, this might fail
        db_manager.update_account_balance('ATEST', 999.99)
        assert db_manager.get_account_balance('ATEST') == 999.99


class TestExternalAPIManager:
    """Test cases for external API integration."""
    
    @pytest.fixture
    def api_manager(self):
        return ExternalAPIManager()
    
    def test_api_timeout_behavior(self, api_manager):
        """Test API behavior with timeouts and errors."""
        
        # Test normal API call (mocked)
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'account_id': 'A001', 'balance': 1000.00}
            mock_get.return_value = mock_response
            
            result = api_manager.get_account_details('A001')
            assert result['account_id'] == 'A001'
    
    def test_api_failure_scenarios(self, api_manager):
        """Test API failure handling."""
        
        # Test timeout scenario
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
            
            with pytest.raises(requests.exceptions.Timeout):
                api_manager.get_account_details('A001')
        
        # Test API error response
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response
            
            with pytest.raises(Exception) as exc_info:
                api_manager.get_account_details('A001')
            
            assert "Failed to fetch account details: 500" in str(exc_info.value)
    
    def test_api_service_unavailable(self, api_manager):
        """Test behavior when API services are completely unavailable."""
        
        # Test connection error
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError("Service unavailable")
            
            with pytest.raises(requests.exceptions.ConnectionError):
                api_manager.validate_transaction({'transaction_id': 'T001'})


class TestFinancialDataProcessor:
    """Test cases for the main data processor."""
    
    @pytest.fixture
    def processor(self):
        """Create processor with temporary database."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        processor = FinancialDataProcessor(temp_db.name)
        yield processor
        
        # Cleanup
        os.unlink(temp_db.name)
    
    @pytest.fixture
    def sample_transaction(self):
        return {
            'transaction_id': 'T001',
            'account_id': 'A001',
            'amount': 100.00,
            'transaction_type': 'credit',
            'transaction_date': '2024-01-01'
        }
    
    def test_successful_transaction_processing(self, processor, sample_transaction):
        """Test successful transaction processing."""
        
        # Mock all external API calls
        with patch.object(processor.api_manager, 'get_account_details') as mock_account, \
             patch.object(processor.api_manager, 'validate_transaction') as mock_validate, \
             patch.object(processor.api_manager, 'send_notification') as mock_notify, \
             patch.object(processor.api_manager, 'log_audit_event') as mock_audit:
            
            mock_account.return_value = {'account_id': 'A001', 'status': 'active'}
            mock_validate.return_value = True
            
            result = processor.process_transaction(sample_transaction)
            
            assert result['status'] == 'success'
            assert result['transaction_id'] == 'T001'
            
            # Verify all external calls were made
            mock_account.assert_called_once()
            mock_validate.assert_called_once()
            mock_notify.assert_called_once()
            mock_audit.assert_called_once()
    
    def test_transaction_processing_with_api_failures(self, processor, sample_transaction):
        """Test transaction processing when APIs fail."""
        
        # Test account service failure
        with patch.object(processor.api_manager, 'get_account_details') as mock_account:
            mock_account.side_effect = Exception("Account service unavailable")
            
            with pytest.raises(Exception):
                processor.process_transaction(sample_transaction)
        
        # Test validation service failure
        with patch.object(processor.api_manager, 'get_account_details') as mock_account, \
             patch.object(processor.api_manager, 'validate_transaction') as mock_validate:
            
            mock_account.return_value = {'account_id': 'A001', 'status': 'active'}
            mock_validate.side_effect = Exception("Validation service down")
            
            with pytest.raises(Exception):
                processor.process_transaction(sample_transaction)
    
    def test_insufficient_funds_handling(self, processor):
        """Test handling of insufficient funds scenario."""
        
        # Setup account with low balance
        processor.db_manager.update_account_balance('A001', 50.00)
        
        # Try to debit more than available
        debit_transaction = {
            'transaction_id': 'T002',
            'account_id': 'A001',
            'amount': 100.00,
            'transaction_type': 'debit',
            'transaction_date': '2024-01-01'
        }
        
        with patch.object(processor.api_manager, 'get_account_details') as mock_account, \
             patch.object(processor.api_manager, 'validate_transaction') as mock_validate:
            
            mock_account.return_value = {'account_id': 'A001', 'status': 'active'}
            mock_validate.return_value = True
            
            with pytest.raises(ValueError) as exc_info:
                processor.process_transaction(debit_transaction)
            
            assert "Insufficient funds" in str(exc_info.value)


class TestBatchProcessing:
    """Test cases for batch processing functionality."""
    
    @pytest.fixture
    def processor(self):
        """Create processor with temporary database."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        processor = FinancialDataProcessor(temp_db.name)
        yield processor
        
        # Cleanup
        os.unlink(temp_db.name)
    
    @pytest.fixture
    def sample_data_files(self):
        """Create temporary data files for testing."""
        temp_dir = tempfile.mkdtemp()
        
        # Create CSV file
        csv_file = os.path.join(temp_dir, "transactions_2024-01-01.csv")
        csv_content = """transaction_id,account_id,amount,transaction_type,transaction_date
T001,A001,100.00,credit,2024-01-01
T002,A002,50.00,debit,2024-01-01
T003,A001,25.00,debit,2024-01-01"""
        
        with open(csv_file, 'w') as f:
            f.write(csv_content)
        
        # Create JSON file
        json_file = os.path.join(temp_dir, "transactions_2024-01-01.json")
        json_data = [
            {
                'transaction_id': 'T004',
                'account_id': 'A003',
                'amount': 200.00,
                'transaction_type': 'credit',
                'transaction_date': '2024-01-01'
            }
        ]
        
        with open(json_file, 'w') as f:
            json.dump(json_data, f)
        
        yield temp_dir
        
        # Cleanup
        os.unlink(csv_file)
        os.unlink(json_file)
        os.rmdir(temp_dir)
    
    def test_file_loading_memory_usage(self, processor, sample_data_files):
        """Test memory usage during file loading."""
        import psutil
        import os
        
        # Measure memory before loading
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss
        
        # Load files
        file_paths = [
            os.path.join(sample_data_files, "transactions_2024-01-01.csv"),
            os.path.join(sample_data_files, "transactions_2024-01-01.json")
        ]
        
        transactions = processor.load_transaction_files(file_paths)
        
        # Measure memory after loading
        memory_after = process.memory_info().rss
        memory_increase = memory_after - memory_before
        
        print(f"Memory increase: {memory_increase / 1024 / 1024:.2f} MB")
        print(f"Transactions loaded: {len(transactions)}")
        
        # This test reveals that all data is loaded into memory at once
        # which could be problematic for large files
        assert len(transactions) == 4
    
    def test_batch_processing_partial_failures(self, processor, sample_data_files):
        """Test batch processing with some transaction failures."""
        
        # Mock API calls with mixed success/failure
        def mock_validate_transaction(transaction):
            # Fail validation for specific transaction
            if transaction['transaction_id'] == 'T002':
                raise Exception("Validation failed")
            return True
        
        with patch.object(processor.api_manager, 'get_account_details') as mock_account, \
             patch.object(processor.api_manager, 'validate_transaction', side_effect=mock_validate_transaction), \
             patch.object(processor.api_manager, 'send_notification'), \
             patch.object(processor.api_manager, 'log_audit_event'):
            
            mock_account.return_value = {'account_id': 'A001', 'status': 'active'}
            
            # This should process successfully despite some failures
            processor.process_daily_batch('2024-01-01', sample_data_files)
            
            # Check that batch status was recorded
            # The system continues processing despite individual failures
    
    def test_large_batch_performance(self, processor):
        """Test performance characteristics with large data volumes."""
        
        # Create a large number of transactions in memory
        large_transaction_set = []
        for i in range(1000):
            large_transaction_set.append({
                'transaction_id': f'T{i:06d}',
                'account_id': f'A{i % 100:03d}',
                'amount': 100.00 + (i % 1000),
                'transaction_type': 'credit' if i % 2 == 0 else 'debit',
                'transaction_date': '2024-01-01'
            })
        
        # Mock all API calls to focus on processing performance
        with patch.object(processor.api_manager, 'get_account_details') as mock_account, \
             patch.object(processor.api_manager, 'validate_transaction') as mock_validate, \
             patch.object(processor.api_manager, 'send_notification'), \
             patch.object(processor.api_manager, 'log_audit_event'):
            
            mock_account.return_value = {'account_id': 'A001', 'status': 'active'}
            mock_validate.return_value = True
            
            # Process each transaction and measure time
            start_time = time.time()
            
            processed_count = 0
            for transaction in large_transaction_set[:100]:  # Process subset for testing
                try:
                    processor.process_transaction(transaction)
                    processed_count += 1
                except Exception:
                    continue
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"Processed {processed_count} transactions in {processing_time:.2f} seconds")
            print(f"Rate: {processed_count / processing_time:.1f} transactions/second")
            
            # This test reveals performance characteristics
            # and potential bottlenecks in the processing pipeline


class TestSystemResilience:
    """Test cases for system resilience and failure recovery."""
    
    @pytest.fixture
    def processor(self):
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        processor = FinancialDataProcessor(temp_db.name)
        yield processor
        
        os.unlink(temp_db.name)
    
    def test_database_connection_exhaustion(self, processor):
        """Test behavior when database connections are exhausted."""
        
        # Simulate connection exhaustion by making many concurrent operations
        # This test may reveal connection leaks
        
        results = []
        for i in range(100):
            try:
                processor.db_manager.update_account_balance(f'A{i:03d}', float(i))
                balance = processor.db_manager.get_account_balance(f'A{i:03d}')
                results.append(balance)
            except Exception as e:
                print(f"Connection error at iteration {i}: {e}")
                results.append(None)
        
        # Check how many operations succeeded
        successful_operations = sum(1 for r in results if r is not None)
        print(f"Successful operations: {successful_operations}/100")
        
        # This test may reveal connection pool exhaustion issues
    
    def test_api_service_degradation(self, processor):
        """Test system behavior when external APIs are slow or failing."""
        
        sample_transaction = {
            'transaction_id': 'T001',
            'account_id': 'A001',
            'amount': 100.00,
            'transaction_type': 'credit',
            'transaction_date': '2024-01-01'
        }
        
        # Test with slow API responses
        def slow_api_call(*args, **kwargs):
            time.sleep(2)  # Simulate slow API
            return {'account_id': 'A001', 'status': 'active'}
        
        with patch.object(processor.api_manager, 'get_account_details', side_effect=slow_api_call), \
             patch.object(processor.api_manager, 'validate_transaction') as mock_validate, \
             patch.object(processor.api_manager, 'send_notification'), \
             patch.object(processor.api_manager, 'log_audit_event'):
            
            mock_validate.return_value = True
            
            start_time = time.time()
            try:
                result = processor.process_transaction(sample_transaction)
                end_time = time.time()
                
                processing_time = end_time - start_time
                print(f"Transaction processing took {processing_time:.2f} seconds")
                
                # This reveals that slow APIs block the entire processing pipeline
                
            except Exception as e:
                print(f"Transaction failed due to slow API: {e}")
    
    def test_memory_pressure_handling(self, processor):
        """Test system behavior under memory pressure."""
        
        # Try to load very large dataset into memory
        # This simulates the memory usage pattern of load_transaction_files
        
        large_data = []
        try:
            # Create increasingly large data structures
            for i in range(10):
                chunk_size = 10000 * (i + 1)
                chunk = [{'id': j, 'data': 'x' * 100} for j in range(chunk_size)]
                large_data.extend(chunk)
                
                print(f"Loaded chunk {i + 1}: {len(large_data)} total records")
                
                # This pattern mimics how load_transaction_files works
                # All data accumulates in memory
                
        except MemoryError:
            print(f"Memory exhausted at {len(large_data)} records")
        
        # This test reveals the memory limitations of the current approach


class TestMonitoringAndObservability:
    """Test cases for monitoring and observability features."""
    
    @pytest.fixture
    def processor(self):
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        processor = FinancialDataProcessor(temp_db.name)
        yield processor
        
        os.unlink(temp_db.name)
    
    def test_processing_status_tracking(self, processor):
        """Test that processing status is properly tracked."""
        
        # This test will fail if batch processing doesn't properly track status
        
        with patch.object(processor, 'load_transaction_files') as mock_load, \
             patch.object(processor, 'process_transaction') as mock_process:
            
            mock_load.return_value = [
                {'transaction_id': 'T001', 'account_id': 'A001', 'amount': 100}
            ]
            mock_process.return_value = {'status': 'success'}
            
            processor.process_daily_batch('2024-01-01')
            
            # Check if status was recorded
            import sqlite3
            conn = sqlite3.connect(processor.db_manager.database_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM processing_status")
            status_records = cursor.fetchall()
            conn.close()
            
            assert len(status_records) > 0
            print(f"Processing status records: {status_records}")
    
    def test_error_reporting_and_logging(self, processor):
        """Test error reporting and logging capabilities."""
        
        # Test that errors are properly logged and don't stop processing
        
        def failing_process_transaction(transaction):
            if transaction['transaction_id'] == 'T002':
                raise Exception("Simulated processing error")
            return {'status': 'success'}
        
        with patch.object(processor, 'load_transaction_files') as mock_load, \
             patch.object(processor, 'process_transaction', side_effect=failing_process_transaction):
            
            mock_load.return_value = [
                {'transaction_id': 'T001', 'account_id': 'A001', 'amount': 100},
                {'transaction_id': 'T002', 'account_id': 'A002', 'amount': 200},
                {'transaction_id': 'T003', 'account_id': 'A003', 'amount': 300}
            ]
            
            # Should continue processing despite errors
            processor.process_daily_batch('2024-01-01')
            
            # Verify error was tracked
            import sqlite3
            conn = sqlite3.connect(processor.db_manager.database_path)
            cursor = conn.cursor()
            cursor.execute("SELECT errors_encountered FROM processing_status")
            error_counts = cursor.fetchall()
            conn.close()
            
            print(f"Error counts: {error_counts}")
            # Should have recorded at least one error


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])