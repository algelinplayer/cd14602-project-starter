"""
Code Review Exercise 3: File Processing with Dependencies

Your task: Review this file processing code for dependency and structural issues.
Focus on:
- Library imports and dependencies
- Code structure and error handling
- Function design and testability

Instructions:
1. Verify all imported libraries are valid
2. Check for structural patterns and issues
3. Evaluate error handling approach
4. Rate the overall code quality (Poor, Fair, Good, Excellent)
5. Provide your recommendation (Accept, Modify, Reject)
"""

import os
import pandas as pd

try:
    from advanced_file_processor import FastProcessor
    ADVANCED_PROCESSOR_AVAILABLE = True
except ImportError:
    ADVANCED_PROCESSOR_AVAILABLE = False

try:
    from data_cleaner_pro import clean_dataset
    DATA_CLEANER_AVAILABLE = True
except ImportError:
    DATA_CLEANER_AVAILABLE = False

class MockFastProcessor:
    def __init__(self, optimization_level=1):
        self.optimization_level = optimization_level
    
    def load_file(self, file_path):
        return {"data": "mock file content", "path": file_path}

def mock_clean_dataset(data, method='basic'):
    return {"cleaned": True, "original": data}

def process_uploaded_files(file_paths):
    """Process multiple uploaded files and return cleaned datasets."""
    results = []

    for file_path in file_paths:
        try:
            if ADVANCED_PROCESSOR_AVAILABLE:
                processor = FastProcessor(optimization_level=3)
            else:
                processor = MockFastProcessor(optimization_level=3)
            
            raw_data = processor.load_file(file_path)

            if DATA_CLEANER_AVAILABLE:
                cleaned = clean_dataset(raw_data, method='auto_detect')
            else:
                cleaned = mock_clean_dataset(raw_data, method='auto_detect')

            df = pd.DataFrame(cleaned)
            results.append(df)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue

    return results

def validate_file_paths(file_paths):
    """Validate that all file paths exist and are accessible."""
    valid_paths = []
    for path in file_paths:
        if os.path.exists(path):
            valid_paths.append(path)
        else:
            print(f"Warning: File not found: {path}")
    return valid_paths