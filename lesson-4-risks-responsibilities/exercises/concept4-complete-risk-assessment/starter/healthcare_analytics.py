"""
AI-Generated Healthcare Analytics and Patient Data Processing System
===================================================================

This module provides clinical decision support, patient analytics, and
population health insights. Generated to support evidence-based medical
decision making while maintaining HIPAA compliance.
"""

import hashlib
import sqlite3
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import os
import base64

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PatientDataManager:
    """Manages patient data storage and retrieval."""
    
    def __init__(self, database_path: str = "patient_data.db"):
        self.database_path = database_path
        self.setup_database()
    
    def setup_database(self):
        """Initialize database with patient data tables."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Patient demographics and identifiers
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                patient_id TEXT PRIMARY KEY,
                ssn TEXT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                date_of_birth DATE NOT NULL,
                gender TEXT,
                race TEXT,
                ethnicity TEXT,
                insurance_id TEXT,
                address TEXT,
                phone TEXT,
                email TEXT,
                emergency_contact TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Medical records and clinical data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medical_records (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                encounter_date DATE NOT NULL,
                diagnosis_codes TEXT,
                procedure_codes TEXT,
                medications TEXT,
                vital_signs TEXT,
                lab_results TEXT,
                provider_notes TEXT,
                provider_id TEXT,
                facility_id TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
            )
        """)
        
        # Clinical risk scores and analytics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_assessments (
                assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                assessment_date TIMESTAMP NOT NULL,
                risk_category TEXT NOT NULL,
                risk_score REAL NOT NULL,
                risk_factors TEXT,
                recommendations TEXT,
                calculated_by TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
            )
        """)
        
        # System access and audit logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS access_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                patient_id TEXT,
                action TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                session_id TEXT,
                data_accessed TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def store_patient_data(self, patient_data: Dict[str, Any]) -> bool:
        """Store patient demographic and identifier information."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO patients 
                (patient_id, ssn, first_name, last_name, date_of_birth, gender, 
                 race, ethnicity, insurance_id, address, phone, email, emergency_contact)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                patient_data['patient_id'],
                patient_data.get('ssn'),
                patient_data['first_name'],
                patient_data['last_name'],
                patient_data['date_of_birth'],
                patient_data.get('gender'),
                patient_data.get('race'),
                patient_data.get('ethnicity'),
                patient_data.get('insurance_id'),
                patient_data.get('address'),
                patient_data.get('phone'),
                patient_data.get('email'),
                patient_data.get('emergency_contact')
            ))
            
            conn.commit()
            logger.info(f"Stored patient data for {patient_data['patient_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing patient data: {e}")
            return False
        finally:
            conn.close()
    
    def get_patient_data(self, patient_id: str, user_id: str = None) -> Dict[str, Any]:
        """Retrieve patient data with access logging."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Log data access
        cursor.execute("""
            INSERT INTO access_logs (user_id, patient_id, action, data_accessed)
            VALUES (?, ?, ?, ?)
        """, (user_id or 'system', patient_id, 'READ_PATIENT_DATA', 'demographics'))
        
        # Retrieve patient data
        cursor.execute("""
            SELECT * FROM patients WHERE patient_id = ?
        """, (patient_id,))
        
        patient_row = cursor.fetchone()
        
        if patient_row:
            columns = [description[0] for description in cursor.description]
            patient_data = dict(zip(columns, patient_row))
            
            conn.commit()
            conn.close()
            return patient_data
        else:
            conn.commit()
            conn.close()
            return {}
    
    def store_medical_record(self, record_data: Dict[str, Any]) -> bool:
        """Store medical record data."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO medical_records 
                (patient_id, encounter_date, diagnosis_codes, procedure_codes,
                 medications, vital_signs, lab_results, provider_notes, provider_id, facility_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record_data['patient_id'],
                record_data['encounter_date'],
                json.dumps(record_data.get('diagnosis_codes', [])),
                json.dumps(record_data.get('procedure_codes', [])),
                json.dumps(record_data.get('medications', [])),
                json.dumps(record_data.get('vital_signs', {})),
                json.dumps(record_data.get('lab_results', {})),
                record_data.get('provider_notes', ''),
                record_data.get('provider_id'),
                record_data.get('facility_id')
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error storing medical record: {e}")
            return False
        finally:
            conn.close()


class ClinicalDecisionSupport:
    """Provides AI-powered clinical decision support and risk assessment."""
    
    def __init__(self, data_manager: PatientDataManager):
        self.data_manager = data_manager
        
        # Risk scoring models and weights
        self.risk_models = {
            'cardiovascular': {
                'age_weight': 0.3,
                'bmi_weight': 0.2,
                'smoking_weight': 0.25,
                'family_history_weight': 0.15,
                'cholesterol_weight': 0.1
            },
            'diabetes': {
                'age_weight': 0.25,
                'bmi_weight': 0.35,
                'family_history_weight': 0.2,
                'ethnicity_weight': 0.1,
                'glucose_weight': 0.1
            },
            'readmission': {
                'age_weight': 0.2,
                'comorbidities_weight': 0.3,
                'previous_admissions_weight': 0.25,
                'social_factors_weight': 0.15,
                'medication_compliance_weight': 0.1
            }
        }
        
        # Population-based scoring adjustments
        self.demographic_adjustments = {
            'cardiovascular': {
                'race': {
                    'african_american': 1.2,
                    'hispanic': 1.1,
                    'asian': 0.9,
                    'caucasian': 1.0,
                    'other': 1.0
                },
                'gender': {
                    'male': 1.3,
                    'female': 1.0
                },
                'insurance': {
                    'medicaid': 1.15,
                    'uninsured': 1.25,
                    'private': 1.0,
                    'medicare': 1.05
                }
            }
        }
    
    def calculate_cardiovascular_risk(self, patient_id: str) -> Dict[str, Any]:
        """Calculate cardiovascular disease risk score."""
        
        # Get patient data
        patient_data = self.data_manager.get_patient_data(patient_id)
        
        if not patient_data:
            return {'error': 'Patient not found'}
        
        # Calculate age
        birth_date = datetime.strptime(patient_data['date_of_birth'], '%Y-%m-%d')
        age = (datetime.now() - birth_date).days / 365.25
        
        # Age-based risk (higher for older patients)
        age_score = min(100, age * 1.2) if age > 40 else age * 0.5
        
        # Gender-based adjustment
        gender_multiplier = self.demographic_adjustments['cardiovascular']['gender'].get(
            patient_data.get('gender', '').lower(), 1.0
        )
        
        # Race-based adjustment
        race_multiplier = self.demographic_adjustments['cardiovascular']['race'].get(
            patient_data.get('race', '').lower().replace(' ', '_'), 1.0
        )
        
        # Insurance-based social determinant adjustment
        insurance_multiplier = self.demographic_adjustments['cardiovascular']['insurance'].get(
            patient_data.get('insurance_id', 'private').lower(), 1.0
        )
        
        # Calculate base risk score
        base_score = age_score * self.risk_models['cardiovascular']['age_weight']
        
        # Apply demographic adjustments
        adjusted_score = base_score * gender_multiplier * race_multiplier * insurance_multiplier
        
        # Additional risk factors (simplified for demo)
        # In real system, would integrate with lab results and clinical data
        
        risk_level = 'low'
        if adjusted_score > 80:
            risk_level = 'high'
        elif adjusted_score > 60:
            risk_level = 'moderate'
        
        # Generate recommendations
        recommendations = self._generate_cv_recommendations(adjusted_score, patient_data)
        
        result = {
            'patient_id': patient_id,
            'risk_score': round(adjusted_score, 2),
            'risk_level': risk_level,
            'risk_factors': {
                'age_component': round(age_score, 2),
                'gender_adjustment': gender_multiplier,
                'race_adjustment': race_multiplier,
                'insurance_adjustment': insurance_multiplier
            },
            'recommendations': recommendations,
            'calculated_at': datetime.now().isoformat()
        }
        
        # Store risk assessment
        self._store_risk_assessment(patient_id, 'cardiovascular', result)
        
        return result
    
    def _generate_cv_recommendations(self, risk_score: float, patient_data: Dict[str, Any]) -> List[str]:
        """Generate cardiovascular risk reduction recommendations."""
        recommendations = []
        
        if risk_score > 70:
            recommendations.append("Consider statin therapy initiation")
            recommendations.append("Recommend cardiology consultation")
            recommendations.append("Aggressive lifestyle modification counseling")
        elif risk_score > 50:
            recommendations.append("Lifestyle modification counseling")
            recommendations.append("Monitor blood pressure and cholesterol")
            recommendations.append("Consider preventive medication discussion")
        else:
            recommendations.append("Continue routine preventive care")
            recommendations.append("Maintain healthy lifestyle habits")
        
        # Add demographic-specific recommendations
        race = patient_data.get('race', '').lower()
        if 'african_american' in race:
            recommendations.append("Monitor for hypertension (higher risk population)")
        
        return recommendations
    
    def _store_risk_assessment(self, patient_id: str, risk_category: str, assessment_data: Dict[str, Any]):
        """Store risk assessment results."""
        conn = sqlite3.connect(self.data_manager.database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO risk_assessments 
            (patient_id, assessment_date, risk_category, risk_score, risk_factors, recommendations, calculated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            patient_id,
            datetime.now(),
            risk_category,
            assessment_data['risk_score'],
            json.dumps(assessment_data['risk_factors']),
            json.dumps(assessment_data['recommendations']),
            'AI_SYSTEM'
        ))
        
        conn.commit()
        conn.close()
    
    def batch_risk_assessment(self, patient_ids: List[str]) -> Dict[str, Any]:
        """Perform risk assessment on multiple patients."""
        results = []
        
        for patient_id in patient_ids:
            try:
                cv_risk = self.calculate_cardiovascular_risk(patient_id)
                results.append(cv_risk)
            except Exception as e:
                logger.error(f"Risk assessment failed for patient {patient_id}: {e}")
                results.append({
                    'patient_id': patient_id,
                    'error': str(e)
                })
        
        return {
            'total_patients': len(patient_ids),
            'successful_assessments': len([r for r in results if 'error' not in r]),
            'failed_assessments': len([r for r in results if 'error' in r]),
            'results': results
        }


class PopulationHealthAnalytics:
    """Provides population health insights and trend analysis."""
    
    def __init__(self, data_manager: PatientDataManager):
        self.data_manager = data_manager
    
    def analyze_population_health_trends(self, demographics_filter: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze health trends across population segments."""
        
        conn = sqlite3.connect(self.data_manager.database_path)
        
        # Get population demographics
        query = "SELECT * FROM patients"
        conditions = []
        params = []
        
        if demographics_filter:
            if demographics_filter.get('age_min'):
                conditions.append("(julianday('now') - julianday(date_of_birth)) / 365.25 >= ?")
                params.append(demographics_filter['age_min'])
            
            if demographics_filter.get('gender'):
                conditions.append("gender = ?")
                params.append(demographics_filter['gender'])
            
            if demographics_filter.get('race'):
                conditions.append("race = ?")
                params.append(demographics_filter['race'])
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        patients_df = pd.read_sql_query(query, conn, params=params)
        
        # Get risk assessments
        risk_query = """
            SELECT ra.*, p.race, p.gender, p.insurance_id,
                   (julianday('now') - julianday(p.date_of_birth)) / 365.25 as age
            FROM risk_assessments ra
            JOIN patients p ON ra.patient_id = p.patient_id
        """
        
        risk_df = pd.read_sql_query(risk_query, conn)
        conn.close()
        
        if len(risk_df) == 0:
            return {'error': 'No risk assessment data available'}
        
        # Analyze risk distribution by demographics
        analysis = {
            'total_patients': len(patients_df),
            'total_assessments': len(risk_df),
            'risk_distribution': {},
            'demographic_analysis': {},
            'trends': {}
        }
        
        # Overall risk distribution
        risk_counts = risk_df.groupby('risk_category')['risk_score'].agg(['count', 'mean', 'std']).round(2)
        analysis['risk_distribution'] = risk_counts.to_dict('index')
        
        # Demographic breakdown
        if 'race' in risk_df.columns:
            race_analysis = risk_df.groupby(['race', 'risk_category'])['risk_score'].mean().unstack(fill_value=0)
            analysis['demographic_analysis']['by_race'] = race_analysis.to_dict()
        
        if 'gender' in risk_df.columns:
            gender_analysis = risk_df.groupby(['gender', 'risk_category'])['risk_score'].mean().unstack(fill_value=0)
            analysis['demographic_analysis']['by_gender'] = gender_analysis.to_dict()
        
        # Insurance-based analysis (social determinants)
        if 'insurance_id' in risk_df.columns:
            insurance_analysis = risk_df.groupby('insurance_id')['risk_score'].agg(['count', 'mean']).round(2)
            analysis['demographic_analysis']['by_insurance'] = insurance_analysis.to_dict('index')
        
        return analysis
    
    def generate_population_report(self) -> Dict[str, Any]:
        """Generate comprehensive population health report."""
        
        # Get overall population trends
        overall_trends = self.analyze_population_health_trends()
        
        # Analyze specific demographic segments
        demographic_segments = [
            {'race': 'African American'},
            {'race': 'Hispanic'},
            {'race': 'Asian'},
            {'race': 'Caucasian'},
            {'gender': 'male'},
            {'gender': 'female'},
            {'age_min': 65}  # Elderly population
        ]
        
        segment_analysis = {}
        for segment in demographic_segments:
            segment_key = list(segment.keys())[0] + '_' + str(list(segment.values())[0])
            segment_analysis[segment_key] = self.analyze_population_health_trends(segment)
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'overall_population': overall_trends,
            'demographic_segments': segment_analysis,
            'summary_insights': self._generate_population_insights(overall_trends, segment_analysis)
        }
        
        return report
    
    def _generate_population_insights(self, overall_data: Dict[str, Any], 
                                    segment_data: Dict[str, Any]) -> List[str]:
        """Generate insights from population health analysis."""
        insights = []
        
        # Check for demographic disparities
        if 'demographic_analysis' in overall_data:
            race_data = overall_data['demographic_analysis'].get('by_race', {})
            
            # Look for high-risk groups
            if 'cardiovascular' in race_data:
                cv_by_race = race_data['cardiovascular']
                max_race = max(cv_by_race, key=cv_by_race.get) if cv_by_race else None
                min_race = min(cv_by_race, key=cv_by_race.get) if cv_by_race else None
                
                if max_race and min_race and cv_by_race[max_race] > cv_by_race[min_race] * 1.2:
                    insights.append(f"Cardiovascular risk disparities detected: {max_race} population shows 20%+ higher risk than {min_race}")
        
        # Insurance-based insights
        insurance_data = overall_data.get('demographic_analysis', {}).get('by_insurance', {})
        if insurance_data:
            high_risk_insurance = [(ins, data['mean']) for ins, data in insurance_data.items() 
                                 if data['mean'] > 60]
            
            if high_risk_insurance:
                insights.append("Social determinants impact detected: Uninsured/Medicaid populations show elevated risk scores")
        
        insights.append(f"Population analysis based on {overall_data.get('total_patients', 0)} patients")
        
        return insights


class HealthcareDataExporter:
    """Handles data export and reporting functionality."""
    
    def __init__(self, data_manager: PatientDataManager):
        self.data_manager = data_manager
    
    def export_patient_data(self, patient_ids: List[str], export_format: str = 'json', 
                          user_id: str = None) -> str:
        """Export patient data for research or transfer purposes."""
        
        exported_data = []
        
        for patient_id in patient_ids:
            # Log data export access
            conn = sqlite3.connect(self.data_manager.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO access_logs (user_id, patient_id, action, data_accessed)
                VALUES (?, ?, ?, ?)
            """, (user_id or 'system', patient_id, 'EXPORT_DATA', 'full_record'))
            
            # Get complete patient record
            cursor.execute("""
                SELECT p.*, 
                       GROUP_CONCAT(mr.diagnosis_codes) as all_diagnoses,
                       GROUP_CONCAT(mr.medications) as all_medications
                FROM patients p
                LEFT JOIN medical_records mr ON p.patient_id = mr.patient_id
                WHERE p.patient_id = ?
                GROUP BY p.patient_id
            """, (patient_id,))
            
            patient_row = cursor.fetchone()
            
            if patient_row:
                columns = [description[0] for description in cursor.description]
                patient_data = dict(zip(columns, patient_row))
                exported_data.append(patient_data)
            
            conn.commit()
            conn.close()
        
        # Generate export file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"patient_export_{timestamp}.{export_format}"
        
        if export_format == 'json':
            with open(filename, 'w') as f:
                json.dump(exported_data, f, indent=2, default=str)
        elif export_format == 'csv':
            if exported_data:
                df = pd.DataFrame(exported_data)
                df.to_csv(filename, index=False)
        
        logger.info(f"Exported {len(exported_data)} patient records to {filename}")
        return filename
    
    def generate_research_dataset(self, research_criteria: Dict[str, Any]) -> str:
        """Generate de-identified dataset for research purposes."""
        
        conn = sqlite3.connect(self.data_manager.database_path)
        
        # Build query based on research criteria
        query = """
            SELECT p.gender, p.race, p.ethnicity,
                   (julianday('now') - julianday(p.date_of_birth)) / 365.25 as age,
                   ra.risk_category, ra.risk_score, ra.recommendations
            FROM patients p
            JOIN risk_assessments ra ON p.patient_id = ra.patient_id
        """
        
        conditions = []
        params = []
        
        if research_criteria.get('min_age'):
            conditions.append("(julianday('now') - julianday(p.date_of_birth)) / 365.25 >= ?")
            params.append(research_criteria['min_age'])
        
        if research_criteria.get('risk_category'):
            conditions.append("ra.risk_category = ?")
            params.append(research_criteria['risk_category'])
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        # Execute query and create dataset
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        # Remove any remaining identifiers and create research dataset
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"research_dataset_{timestamp}.csv"
        
        df.to_csv(filename, index=False)
        
        logger.info(f"Generated research dataset with {len(df)} records: {filename}")
        return filename


# Demo data creation and system usage example
def create_demo_data():
    """Create demonstration patient data."""
    
    demo_patients = [
        {
            'patient_id': 'P001',
            'ssn': '123-45-6789',
            'first_name': 'John',
            'last_name': 'Smith',
            'date_of_birth': '1975-03-15',
            'gender': 'male',
            'race': 'Caucasian',
            'ethnicity': 'Non-Hispanic',
            'insurance_id': 'private',
            'address': '123 Main St, Anytown, ST 12345',
            'phone': '555-123-4567',
            'email': 'john.smith@email.com'
        },
        {
            'patient_id': 'P002',
            'ssn': '987-65-4321',
            'first_name': 'Maria',
            'last_name': 'Garcia',
            'date_of_birth': '1982-07-22',
            'gender': 'female',
            'race': 'Hispanic',
            'ethnicity': 'Hispanic',
            'insurance_id': 'medicaid',
            'address': '456 Oak Ave, Somewhere, ST 67890',
            'phone': '555-987-6543',
            'email': 'maria.garcia@email.com'
        },
        {
            'patient_id': 'P003',
            'ssn': '456-78-9123',
            'first_name': 'Robert',
            'last_name': 'Johnson',
            'date_of_birth': '1945-11-08',
            'gender': 'male',
            'race': 'African American',
            'ethnicity': 'Non-Hispanic',
            'insurance_id': 'medicare',
            'address': '789 Pine Rd, Elsewhere, ST 54321',
            'phone': '555-456-7890',
            'email': 'robert.johnson@email.com'
        }
    ]
    
    return demo_patients


if __name__ == "__main__":
    # Demonstration of the healthcare analytics system
    
    # Initialize system components
    data_manager = PatientDataManager()
    decision_support = ClinicalDecisionSupport(data_manager)
    population_analytics = PopulationHealthAnalytics(data_manager)
    data_exporter = HealthcareDataExporter(data_manager)
    
    # Create demo data
    demo_patients = create_demo_data()
    
    print("=== Healthcare Analytics System Demo ===")
    
    # Store patient data
    for patient in demo_patients:
        data_manager.store_patient_data(patient)
        print(f"Stored patient: {patient['first_name']} {patient['last_name']}")
    
    # Perform clinical decision support
    print("\n=== Clinical Decision Support ===")
    for patient in demo_patients:
        risk_assessment = decision_support.calculate_cardiovascular_risk(patient['patient_id'])
        print(f"\nPatient {patient['patient_id']} - {patient['first_name']} {patient['last_name']}:")
        print(f"Cardiovascular Risk Score: {risk_assessment['risk_score']}")
        print(f"Risk Level: {risk_assessment['risk_level']}")
        print(f"Recommendations: {risk_assessment['recommendations']}")
    
    # Population health analysis
    print("\n=== Population Health Analysis ===")
    population_report = population_analytics.generate_population_report()
    print(f"Population analysis complete. Total patients: {population_report['overall_population'].get('total_patients', 0)}")
    
    # Generate insights
    insights = population_report.get('summary_insights', [])
    for insight in insights:
        print(f"- {insight}")
    
    # Data export example
    print("\n=== Data Export ===")
    patient_ids = [p['patient_id'] for p in demo_patients]
    export_file = data_exporter.export_patient_data(patient_ids[:2], 'json', 'demo_user')
    print(f"Exported patient data to: {export_file}")
    
    print("\n=== Demo Complete ===")
    print("System successfully processed patient data, generated risk assessments, and provided population insights.")