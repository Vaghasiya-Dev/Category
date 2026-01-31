#!/usr/bin/env python3
"""
Migration script to transfer all data from local JSON files to Redis
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables FIRST before importing kv_store
load_dotenv()

from database.kv_store import JSONStore, kv

# Base directory
BASE_DIR = Path(__file__).parent

# Map of data keys to their JSON file paths
DATA_FILES = {
    'users': 'database/users.json',
    'audiences': 'database/audiences.json',
    'categories': 'categories.json',
    'blog': 'database/blog.json',
    'settings': 'database/settings.json'
}

def check_redis_connection():
    """Check if Redis connection is available"""
    redis_url = os.environ.get('REDIS_URL') or os.environ.get('KV_URL')
    if not redis_url:
        print("❌ Error: No REDIS_URL or KV_URL found in environment variables")
        print("   Please add REDIS_URL to your .env file")
        return False
    
    if not kv:
        print("❌ Error: Could not connect to Redis")
        print(f"   Redis URL: {redis_url[:50]}...")
        return False
    
    print(f"✓ Connected to Redis successfully")
    print(f"  URL: {redis_url[:50]}...")
    return True

def load_json_file(file_path):
    """Load data from JSON file"""
    full_path = BASE_DIR / file_path
    if not full_path.exists():
        print(f"  ⚠ File not found: {file_path}")
        return None
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"  ❌ Error parsing JSON in {file_path}: {e}")
        return None
    except Exception as e:
        print(f"  ❌ Error reading {file_path}: {e}")
        return None

def migrate_data():
    """Migrate all data from local JSON files to Redis"""
    print("\n" + "="*60)
    print("  DATABASE MIGRATION: Local JSON → Redis")
    print("="*60 + "\n")
    
    # Check Redis connection
    if not check_redis_connection():
        return False
    
    print("\n📦 Starting data migration...\n")
    
    migrated = 0
    skipped = 0
    failed = 0
    
    for key, file_path in DATA_FILES.items():
        print(f"🔄 Migrating '{key}'...")
        
        # Load data from JSON file
        data = load_json_file(file_path)
        
        if data is None:
            print(f"  ❌ Failed to load data")
            failed += 1
            continue
        
        if not data:
            print(f"  ⚠ Empty data (skipped)")
            skipped += 1
            continue
        
        # Count items
        item_count = len(data) if isinstance(data, (dict, list)) else 1
        
        # Write to Redis
        try:
            success = JSONStore.write(key, data)
            if success:
                print(f"  ✓ Migrated {item_count} item(s)")
                migrated += 1
            else:
                print(f"  ❌ Failed to write to Redis")
                failed += 1
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed += 1
    
    # Summary
    print("\n" + "="*60)
    print("  MIGRATION SUMMARY")
    print("="*60)
    print(f"  ✓ Migrated: {migrated}")
    print(f"  ⚠ Skipped:  {skipped}")
    print(f"  ❌ Failed:   {failed}")
    print("="*60 + "\n")
    
    if failed > 0:
        print("⚠ Some migrations failed. Please check the errors above.\n")
        return False
    
    print("✓ Migration completed successfully!\n")
    return True

def verify_migration():
    """Verify that data was migrated correctly"""
    print("🔍 Verifying migration...\n")
    
    all_good = True
    for key in DATA_FILES.keys():
        try:
            data = JSONStore.read(key)
            item_count = len(data) if isinstance(data, (dict, list)) else 1
            print(f"  ✓ {key}: {item_count} item(s) in Redis")
        except Exception as e:
            print(f"  ❌ {key}: Error reading from Redis - {e}")
            all_good = False
    
    print()
    return all_good

def show_redis_info():
    """Show Redis database information"""
    if not kv:
        return
    
    try:
        print("\n📊 Redis Database Info:")
        print("="*60)
        
        # Get all keys
        all_keys = kv.keys('*')
        print(f"  Total keys in Redis: {len(all_keys)}")
        
        if all_keys:
            print("\n  Keys found:")
            for key in sorted(all_keys):
                try:
                    data = kv.get(key)
                    if data:
                        parsed = json.loads(data) if isinstance(data, str) else data
                        size = len(parsed) if isinstance(parsed, (dict, list)) else 1
                        print(f"    • {key}: {size} item(s)")
                except:
                    print(f"    • {key}: (data present)")
        
        print("="*60 + "\n")
    except Exception as e:
        print(f"  Error getting Redis info: {e}\n")

if __name__ == '__main__':
    print("\n🚀 Database Migration Tool")
    print("   This will copy all data from local JSON files to Redis\n")
    
    # Show warning
    print("⚠ WARNING: This will overwrite any existing data in Redis!")
    confirm = input("   Continue? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("\n❌ Migration cancelled.\n")
        exit(0)
    
    # Run migration
    success = migrate_data()
    
    if success:
        # Verify migration
        if verify_migration():
            print("✅ All data verified successfully!")
        else:
            print("⚠ Some verification checks failed.")
        
        # Show Redis info
        show_redis_info()
        
        print("💡 Next steps:")
        print("   1. Restart your Flask application")
        print("   2. The app will now use Redis for all data storage")
        print("   3. Your local JSON files are still intact (backup)\n")
    else:
        print("❌ Migration failed. Please check the errors above.\n")
        exit(1)
