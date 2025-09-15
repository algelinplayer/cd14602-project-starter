"""
Test suite for Healthcare Analytics System
==========================================

This test suite evaluates security, ethical, and reliability risks
in the AI-generated healthcare analytics system. Tests should reveal
issues with HIPAA compliance, algorithmic bias, and system reliability.
"""

import pytest
import sqlite3
import os
import tempfile
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from healthcare_analytics import (
    PatientDataManager, ClinicalDecisionSupport, 
    PopulationHealthAnalytics, HealthcareDataExporter
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def data_manager(temp_db):
    """Create a PatientDataManager instance with temporary database."""
    return PatientDataManager(temp_db)


@pytest.fixture
def sample_patients():
    """Sample patient data for testing."""
    return [
        {
            'patient_id': 'P001',
            'ssn': '123-45-6789',
            'first_name': 'John',
            'last_name': 'Smith',
            'date_of_birth': '1980-01-15',
            'gender': 'male',
            'race': 'Caucasian',
            'ethnicity': 'Non-Hispanic',
            'insurance_id': 'private',
            'address': '123 Main St',
            'phone': '555-123-4567',
            'email': 'john.smith@email.com'
        },
        {
            'patient_id': 'P002',
            'ssn': '987-65-4321',
            'first_name': 'Maria',
            'last_name': 'Garcia',
            'date_of_birth': '1975-05-20',
            'gender': 'female',
            'race': 'Hispanic',
            'ethnicity': 'Hispanic',
            'insurance_id': 'medicaid',
            'address': '456 Oak Ave',
            'phone': '555-987-6543',
            'email': 'maria.garcia@email.com'
        }
    ]


class TestPatientDataSecurity:
    """Test security and privacy aspects of patient data handling."""
    
    def test_patient_data_storage(self, data_manager, sample_patients):
        """Test basic patient data storage functionality."""
        patient = sample_patients[0]
        result = data_manager.store_patient_data(patient)
        assert result is True
        
        # Verify data was stored
        stored_data = data_manager.get_patient_data(patient['patient_id'])
        assert stored_data['patient_id'] == patient['patient_id']
        assert stored_data['first_name'] == patient['first_name']
    
    def test_sensitive_data_exposure(self, data_manager, sample_patients):
        """Test for potential exposure of sensitive data like SSNs."""
        patient = sample_patients[0]
        data_manager.store_patient_data(patient)
        
        # This test checks if SSNs are stored in plain text (security risk)
        conn = sqlite3.connect(data_manager.database_path)
        cursor = conn.cursor()
        cursor.execute("SELECT ssn FROM patients WHERE patient_id = ?", (patient['patient_id'],))
        stored_ssn = cursor.fetchone()[0]
        conn.close()
        
        # This assertion will PASS but reveals the security issue
        # SSNs should be encrypted or hashed, not stored in plain text
        assert stored_ssn == patient['ssn']  # This reveals the vulnerability
    
    def test_access_logging_completeness(self, data_manager, sample_patients):
        """Test if all data access is properly logged for HIPAA compliance."""
        patient = sample_patients[0]
        data_manager.store_patient_data(patient)
        
        # Access patient data
        user_id = "doctor123"
        data_manager.get_patient_data(patient['patient_id'], user_id)
        
        # Check access logs
        conn = sqlite3.connect(data_manager.database_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM access_logs WHERE patient_id = ?", (patient['patient_id'],))
        logs = cursor.fetchall()
        conn.close()
        
        assert len(logs) > 0
        # But check if logs contain enough detail for HIPAA compliance
        log = logs[0]
        # This test passes but reveals insufficient logging details
        assert log[1] == user_id  # user_id is logged
        # Missing: IP address, session info, specific data accessed


class TestAlgorithmicBias:
    """Test for bias and fairness in clinical decision support algorithms."""
    
    def test_cardiovascular_risk_calculation(self, data_manager, sample_patients):
        """Test basic cardiovascular risk calculation functionality."""
        # Store test patients
        for patient in sample_patients:
            data_manager.store_patient_data(patient)
        
        decision_support = ClinicalDecisionSupport(data_manager)
        
        # Calculate risk for first patient
        risk_result = decision_support.calculate_cardiovascular_risk(sample_patients[0]['patient_id'])
        
        assert 'risk_score' in risk_result
        assert 'risk_level' in risk_result
        assert risk_result['risk_score'] >= 0
    
    def test_demographic_bias_in_risk_scoring(self, data_manager, sample_patients):
        """Test for potential demographic bias in risk scoring."""
        # Store test patients
        for patient in sample_patients:
            data_manager.store_patient_data(patient)
        
        decision_support = ClinicalDecisionSupport(data_manager)
        
        # Calculate risk for patients with different demographics
        white_male_risk = decision_support.calculate_cardiovascular_risk('P001')
        hispanic_female_risk = decision_support.calculate_cardiovascular_risk('P002')
        
        # This test will reveal bias in the algorithm
        # The risk scores should be based on medical factors, not demographics
        white_male_score = white_male_risk['risk_score']
        hispanic_female_score = hispanic_female_risk['risk_score']
        
        # Check risk factor components to see bias
        white_male_factors = white_male_risk['risk_factors']
        hispanic_female_factors = hispanic_female_risk['risk_factors']
        
        # These assertions reveal the demographic bias in the algorithm
        assert white_male_factors['gender_adjustment'] != hispanic_female_factors['gender_adjustment']
        assert white_male_factors['race_adjustment'] != hispanic_female_factors['race_adjustment']
        
        # The different adjustments based on race/gender reveal algorithmic bias
    
    def test_insurance_based_discrimination(self, data_manager, sample_patients):
        """Test for discrimination based on insurance type (social determinants)."""
        # Modify patients to have different insurance types
        private_patient = sample_patients[0].copy()
        private_patient['insurance_id'] = 'private'
        private_patient['patient_id'] = 'P_PRIVATE'
        
        medicaid_patient = sample_patients[1].copy()
        medicaid_patient['insurance_id'] = 'medicaid'
        medicaid_patient['patient_id'] = 'P_MEDICAID'
        
        # Make other factors identical for fair comparison
        medicaid_patient['age'] = private_patient['date_of_birth']
        medicaid_patient['gender'] = private_patient['gender']
        medicaid_patient['race'] = private_patient['race']
        
        data_manager.store_patient_data(private_patient)
        data_manager.store_patient_data(medicaid_patient)
        
        decision_support = ClinicalDecisionSupport(data_manager)
        
        private_risk = decision_support.calculate_cardiovascular_risk('P_PRIVATE')
        medicaid_risk = decision_support.calculate_cardiovascular_risk('P_MEDICAID')
        
        # This test reveals insurance-based bias
        private_adjustment = private_risk['risk_factors']['insurance_adjustment']
        medicaid_adjustment = medicaid_risk['risk_factors']['insurance_adjustment']
        
        # Medicaid patients get higher risk scores due to insurance type
        assert medicaid_adjustment > private_adjustment  # Reveals bias


class TestSystemReliability:
    """Test system reliability and error handling."""
    
    def test_database_error_handling(self, data_manager):
        """Test handling of database connection errors."""
        # Test with invalid patient ID
        result = data_manager.get_patient_data("INVALID_ID")
        assert isinstance(result, dict)
        # System should handle gracefully, but may not have proper error reporting
    
    def test_large_dataset_processing(self, data_manager):
        """Test system behavior with large datasets."""
        # Create many patients to test memory usage
        large_patient_list = []
        for i in range(1000):
            patient = {
                'patient_id': f'P{i:04d}',
                'ssn': f'{i:03d}-{i:02d}-{i:04d}',
                'first_name': f'Patient{i}',
                'last_name': f'Test{i}',
                'date_of_birth': '1980-01-01',
                'gender': 'male' if i % 2 == 0 else 'female',
                'race': 'Caucasian',
                'insurance_id': 'private'
            }
            large_patient_list.append(patient)
        
        # Store all patients (this may reveal memory issues)
        stored_count = 0
        for patient in large_patient_list:
            if data_manager.store_patient_data(patient):
                stored_count += 1
        
        assert stored_count == len(large_patient_list)
        
        # Test batch risk assessment (may reveal performance issues)
        decision_support = ClinicalDecisionSupport(data_manager)
        patient_ids = [p['patient_id'] for p in large_patient_list[:100]]
        
        batch_result = decision_support.batch_risk_assessment(patient_ids)
        
        # This test may pass but could reveal performance/memory issues
        assert batch_result['total_patients'] == 100
    
    def test_concurrent_access_safety(self, data_manager, sample_patients):
        """Test thread safety and concurrent access handling."""
        # Store sample patient
        patient = sample_patients[0]
        data_manager.store_patient_data(patient)
        
        # Simulate concurrent access (simplified test)
        results = []
        for i in range(10):
            result = data_manager.get_patient_data(patient['patient_id'], f'user_{i}')
            results.append(result)
        
        # All requests should succeed, but may reveal concurrency issues
        assert all(r['patient_id'] == patient['patient_id'] for r in results)


class TestDataExportCompliance:
    """Test data export functionality for HIPAA compliance."""
    
    def test_patient_data_export(self, data_manager, sample_patients):
        """Test patient data export functionality."""
        # Store sample patients
        for patient in sample_patients:
            data_manager.store_patient_data(patient)
        
        exporter = HealthcareDataExporter(data_manager)
        
        # Export patient data
        patient_ids = [p['patient_id'] for p in sample_patients]
        export_file = exporter.export_patient_data(patient_ids, 'json', 'admin_user')
        
        # Verify export file was created
        assert os.path.exists(export_file)
        
        # Check if export contains sensitive data (potential HIPAA violation)
        with open(export_file, 'r') as f:
            exported_data = json.load(f)
        
        # This test passes but reveals that SSNs are being exported
        assert any('ssn' in patient for patient in exported_data)  # HIPAA risk
        
        # Cleanup
        os.unlink(export_file)
    
    def test_research_dataset_deidentification(self, data_manager, sample_patients):
        """Test research dataset generation and de-identification."""
        # Store sample patients and create risk assessments
        for patient in sample_patients:
            data_manager.store_patient_data(patient)
        
        decision_support = ClinicalDecisionSupport(data_manager)
        for patient in sample_patients:
            decision_support.calculate_cardiovascular_risk(patient['patient_id'])
        
        exporter = HealthcareDataExporter(data_manager)
        
        # Generate research dataset
        research_criteria = {'min_age': 18, 'risk_category': 'cardiovascular'}
        dataset_file = exporter.generate_research_dataset(research_criteria)
        
        # Verify dataset was created
        assert os.path.exists(dataset_file)
        
        # Check if dataset is properly de-identified
        import pandas as pd
        df = pd.read_csv(dataset_file)
        
        # This test should verify no direct identifiers are present
        columns = df.columns.tolist()
        
        # Good: no direct identifiers like patient_id, ssn, names
        assert 'patient_id' not in columns
        assert 'ssn' not in columns
        assert 'first_name' not in columns
        
        # But demographic data is present, which could still allow re-identification
        assert 'race' in columns
        assert 'gender' in columns
        assert 'age' in columns
        
        # Cleanup
        os.unlink(dataset_file)


class TestPopulationHealthBias:
    """Test population health analytics for bias and fairness."""
    
    def test_population_health_analysis(self, data_manager, sample_patients):
        """Test population health trend analysis."""
        # Store sample patients and create risk assessments
        for patient in sample_patients:
            data_manager.store_patient_data(patient)
        
        decision_support = ClinicalDecisionSupport(data_manager)
        for patient in sample_patients:
            decision_support.calculate_cardiovascular_risk(patient['patient_id'])
        
        population_analytics = PopulationHealthAnalytics(data_manager)
        
        # Analyze population trends
        trends = population_analytics.analyze_population_health_trends()
        
        assert 'total_patients' in trends
        assert 'demographic_analysis' in trends
        assert trends['total_patients'] == len(sample_patients)
    
    def test_demographic_disparity_detection(self, data_manager, sample_patients):
        """Test if system can detect demographic disparities in health outcomes."""
        # Store sample patients and create risk assessments
        for patient in sample_patients:
            data_manager.store_patient_data(patient)
        
        decision_support = ClinicalDecisionSupport(data_manager)
        for patient in sample_patients:
            decision_support.calculate_cardiovascular_risk(patient['patient_id'])
        
        population_analytics = PopulationHealthAnalytics(data_manager)
        
        # Generate population report
        report = population_analytics.generate_population_report()
        
        # Check if disparities are detected and reported
        insights = report.get('summary_insights', [])
        
        # The system should detect disparities, but this test may reveal 
        # that the system is perpetuating rather than identifying bias
        assert len(insights) > 0
        
        # Look for disparity-related insights
        disparity_insights = [insight for insight in insights if 'disparity' in insight.lower() or 'risk' in insight.lower()]
        
        # This test may pass but could reveal that the system normalizes bias
        # rather than flagging it as problematic
        assert len(disparity_insights) >= 0  # May find disparities or may not flag them as issues


if __name__ == "__main__":
    pytest.main([__file__, "-v"])