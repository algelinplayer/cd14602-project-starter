"""
AI-Generated Financial Data Processing Pipeline
==============================================

This module provides batch processing and API integration functionality
for financial data operations. Generated to handle daily data processing
and maintain consistency across multiple data sources.
"""

import json
import sqlite3
import requests
import time
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
import logging

# Basic logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Handles database operations for financial data."""
    
    def __init__(self, database_path: str = "financial_data.db"):
        self.database_path = database_path
        self.setup_database()
    
    def setup_database(self):
        """Initialize database with required tables."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Financial transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT UNIQUE NOT NULL,
                account_id TEXT NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                transaction_type TEXT NOT NULL,
                transaction_date DATE NOT NULL,
                processed_date TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        """)
        
        # Account balances table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS account_balances (
                account_id TEXT PRIMARY KEY,
                current_balance DECIMAL(10,2) NOT NULL,
                last_updated TIMESTAMP NOT NULL
            )
        """)
        
        # Processing status tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processing_status (
                batch_id TEXT PRIMARY KEY,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                records_processed INTEGER DEFAULT 0,
                errors_encountered INTEGER DEFAULT 0,
                status TEXT DEFAULT 'running'
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_transactions(self, transactions: List[Dict[str, Any]]):
        """Save transactions to database."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        for transaction in transactions:
            cursor.execute("""
                INSERT OR REPLACE INTO transactions 
                (transaction_id, account_id, amount, transaction_type, transaction_date, processed_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction['transaction_id'],
                transaction['account_id'],
                transaction['amount'],
                transaction['transaction_type'],
                transaction['transaction_date'],
                datetime.now(),
                'processed'
            ))
        
        conn.commit()
        conn.close()
    
    def update_account_balance(self, account_id: str, new_balance: float):
        """Update account balance."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO account_balances (account_id, current_balance, last_updated)
            VALUES (?, ?, ?)
        """, (account_id, new_balance, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_account_balance(self, account_id: str) -> float:
        """Get current account balance."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT current_balance FROM account_balances WHERE account_id = ?", (account_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else 0.0


class ExternalAPIManager:
    """Manages integration with external financial APIs."""
    
    def __init__(self):
        self.api_endpoints = {
            'account_service': 'https://api.bank.com/accounts',
            'validation_service': 'https://api.validator.com/validate',
            'notification_service': 'https://api.notify.com/send',
            'audit_service': 'https://api.audit.com/log'
        }
        
        self.api_timeouts = {
            'account_service': 30,
            'validation_service': 10,
            'notification_service': 5,
            'audit_service': 15
        }
    
    def get_account_details(self, account_id: str) -> Dict[str, Any]:
        """Fetch account details from external API."""
        url = f"{self.api_endpoints['account_service']}/{account_id}"
        
        response = requests.get(url, timeout=self.api_timeouts['account_service'])
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch account details: {response.status_code}")
    
    def validate_transaction(self, transaction: Dict[str, Any]) -> bool:
        """Validate transaction with external service."""
        url = f"{self.api_endpoints['validation_service']}/transaction"
        
        response = requests.post(url, json=transaction, timeout=self.api_timeouts['validation_service'])
        
        if response.status_code == 200:
            result = response.json()
            return result.get('valid', False)
        else:
            raise Exception(f"Transaction validation failed: {response.status_code}")
    
    def send_notification(self, account_id: str, message: str):
        """Send notification to account holder."""
        url = f"{self.api_endpoints['notification_service']}/notify"
        
        payload = {
            'account_id': account_id,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        response = requests.post(url, json=payload, timeout=self.api_timeouts['notification_service'])
        
        if response.status_code != 200:
            raise Exception(f"Notification failed: {response.status_code}")
    
    def log_audit_event(self, event_type: str, event_data: Dict[str, Any]):
        """Log event to external audit service."""
        url = f"{self.api_endpoints['audit_service']}/events"
        
        audit_payload = {
            'event_type': event_type,
            'event_data': event_data,
            'timestamp': datetime.now().isoformat(),
            'source': 'financial_pipeline'
        }
        
        response = requests.post(url, json=audit_payload, timeout=self.api_timeouts['audit_service'])
        
        if response.status_code != 201:
            raise Exception(f"Audit logging failed: {response.status_code}")


class FinancialDataProcessor:
    """Main processor for financial data pipeline."""
    
    def __init__(self, database_path: str = "financial_data.db"):
        self.db_manager = DatabaseManager(database_path)
        self.api_manager = ExternalAPIManager()
        
    def load_transaction_files(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Load all transaction files into memory."""
        all_transactions = []
        
        for file_path in file_paths:
            if file_path.endswith('.csv'):
                # Load CSV file
                df = pd.read_csv(file_path)
                transactions = df.to_dict('records')
            elif file_path.endswith('.json'):
                # Load JSON file
                with open(file_path, 'r') as f:
                    transactions = json.load(f)
            else:
                continue
            
            # Add all transactions to memory
            all_transactions.extend(transactions)
            logger.info(f"Loaded {len(transactions)} transactions from {file_path}")
        
        logger.info(f"Total transactions loaded: {len(all_transactions)}")
        return all_transactions
    
    def process_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single transaction with full validation and updates."""
        
        # Get current account details
        account_details = self.api_manager.get_account_details(transaction['account_id'])
        
        # Validate transaction
        is_valid = self.api_manager.validate_transaction(transaction)
        
        if not is_valid:
            raise ValueError(f"Transaction validation failed for {transaction['transaction_id']}")
        
        # Calculate new balance
        current_balance = self.db_manager.get_account_balance(transaction['account_id'])
        
        if transaction['transaction_type'] == 'debit':
            new_balance = current_balance - float(transaction['amount'])
        else:
            new_balance = current_balance + float(transaction['amount'])
        
        # Check for negative balance
        if new_balance < 0 and transaction['transaction_type'] == 'debit':
            raise ValueError(f"Insufficient funds for transaction {transaction['transaction_id']}")
        
        # Update database
        self.db_manager.save_transactions([transaction])
        self.db_manager.update_account_balance(transaction['account_id'], new_balance)
        
        # Send notification
        notification_message = f"Transaction {transaction['transaction_id']} processed. New balance: ${new_balance:.2f}"
        self.api_manager.send_notification(transaction['account_id'], notification_message)
        
        # Log audit event
        audit_data = {
            'transaction_id': transaction['transaction_id'],
            'account_id': transaction['account_id'],
            'amount': transaction['amount'],
            'old_balance': current_balance,
            'new_balance': new_balance
        }
        self.api_manager.log_audit_event('TRANSACTION_PROCESSED', audit_data)
        
        return {
            'transaction_id': transaction['transaction_id'],
            'status': 'success',
            'new_balance': new_balance
        }
    
    def process_daily_batch(self, date: str, data_directory: str = "data/"):
        """Process all transactions for a specific date."""
        batch_id = f"batch_{date}_{int(time.time())}"
        
        logger.info(f"Starting batch processing for {date}")
        
        # Find all files for the date
        file_patterns = [
            f"{data_directory}/transactions_{date}.csv",
            f"{data_directory}/transactions_{date}.json",
            f"{data_directory}/daily_batch_{date}.csv"
        ]
        
        existing_files = [f for f in file_patterns if os.path.exists(f)]
        
        if not existing_files:
            logger.warning(f"No transaction files found for date {date}")
            return
        
        # Record batch start
        conn = sqlite3.connect(self.db_manager.database_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO processing_status (batch_id, start_time, status)
            VALUES (?, ?, ?)
        """, (batch_id, datetime.now(), 'running'))
        conn.commit()
        conn.close()
        
        # Load all transactions
        all_transactions = self.load_transaction_files(existing_files)
        
        processed_count = 0
        error_count = 0
        
        # Process each transaction
        for transaction in all_transactions:
            try:
                result = self.process_transaction(transaction)
                processed_count += 1
                
                if processed_count % 100 == 0:
                    logger.info(f"Processed {processed_count} transactions")
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing transaction {transaction.get('transaction_id', 'unknown')}: {e}")
                continue
        
        # Update batch status
        conn = sqlite3.connect(self.db_manager.database_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE processing_status 
            SET end_time = ?, records_processed = ?, errors_encountered = ?, status = ?
            WHERE batch_id = ?
        """, (datetime.now(), processed_count, error_count, 'completed', batch_id))
        conn.commit()
        conn.close()
        
        logger.info(f"Batch {batch_id} completed: {processed_count} processed, {error_count} errors")
    
    def generate_daily_report(self, date: str) -> Dict[str, Any]:
        """Generate summary report for daily processing."""
        
        conn = sqlite3.connect(self.db_manager.database_path)
        cursor = conn.cursor()
        
        # Get transaction summary
        cursor.execute("""
            SELECT 
                COUNT(*) as total_transactions,
                SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE 0 END) as total_credits,
                SUM(CASE WHEN transaction_type = 'debit' THEN amount ELSE 0 END) as total_debits
            FROM transactions 
            WHERE DATE(transaction_date) = ?
        """, (date,))
        
        transaction_summary = cursor.fetchone()
        
        # Get account balance summary
        cursor.execute("""
            SELECT 
                COUNT(*) as accounts_updated,
                SUM(current_balance) as total_balance
            FROM account_balances
        """)
        
        balance_summary = cursor.fetchone()
        
        # Get processing status
        cursor.execute("""
            SELECT 
                COUNT(*) as batches_processed,
                SUM(records_processed) as total_records,
                SUM(errors_encountered) as total_errors
            FROM processing_status 
            WHERE DATE(start_time) = ?
        """, (date,))
        
        processing_summary = cursor.fetchone()
        
        conn.close()
        
        report = {
            'date': date,
            'transactions': {
                'total': transaction_summary[0] if transaction_summary else 0,
                'total_credits': float(transaction_summary[1]) if transaction_summary and transaction_summary[1] else 0.0,
                'total_debits': float(transaction_summary[2]) if transaction_summary and transaction_summary[2] else 0.0
            },
            'accounts': {
                'accounts_updated': balance_summary[0] if balance_summary else 0,
                'total_balance': float(balance_summary[1]) if balance_summary and balance_summary[1] else 0.0
            },
            'processing': {
                'batches_processed': processing_summary[0] if processing_summary else 0,
                'total_records': processing_summary[1] if processing_summary else 0,
                'total_errors': processing_summary[2] if processing_summary else 0
            },
            'generated_at': datetime.now().isoformat()
        }
        
        return report
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old processing data."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        conn = sqlite3.connect(self.db_manager.database_path)
        cursor = conn.cursor()
        
        # Clean old processing status records
        cursor.execute("DELETE FROM processing_status WHERE start_time < ?", (cutoff_date,))
        
        # Clean old transactions (keep financial data longer)
        old_transaction_date = datetime.now() - timedelta(days=days_to_keep * 2)
        cursor.execute("DELETE FROM transactions WHERE processed_date < ?", (old_transaction_date,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Cleaned up data older than {days_to_keep} days")


def run_daily_pipeline(date: str = None):
    """Main entry point for daily processing pipeline."""
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    logger.info(f"Starting daily pipeline for {date}")
    
    processor = FinancialDataProcessor()
    
    try:
        # Process the daily batch
        processor.process_daily_batch(date)
        
        # Generate daily report
        report = processor.generate_daily_report(date)
        
        # Save report
        report_filename = f"reports/daily_report_{date}.json"
        os.makedirs(os.path.dirname(report_filename), exist_ok=True)
        
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Daily report saved to {report_filename}")
        
        # Cleanup old data weekly
        if datetime.now().weekday() == 0:  # Monday
            processor.cleanup_old_data()
        
        logger.info("Daily pipeline completed successfully")
        
    except Exception as e:
        logger.error(f"Daily pipeline failed: {e}")
        raise


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = datetime.now().strftime('%Y-%m-%d')
    
    run_daily_pipeline(date)