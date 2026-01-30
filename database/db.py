"""
Database connection and utilities
"""
import os
from pathlib import Path
 
 
def ensure_database_directory(db_path):
    """
    Ensure database directory exists
    
    Args:
        db_path: Path to database file
    """
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
 
 
def database_exists(db_path):
    """
    Check if database file exists
    
    Args:
        db_path: Path to database file
    
    Returns:
        bool: True if database exists
    """
    return Path(db_path).exists()
 
 
def create_empty_database(db_path):
    """
    Create empty database file
    
    Args:
        db_path: Path to database file
    """
    import json
    ensure_database_directory(db_path)
    
    with open(db_path, 'w') as f:
        json.dump({}, f, indent=2)