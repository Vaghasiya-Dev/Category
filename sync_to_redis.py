#!/usr/bin/env python3
"""
Sync local JSON files to Redis
Run this script once to ensure all local data is synced to Vercel Redis
"""

import os
import json
from database.kv_store import JSONStore, get_kv_connection

def sync_data_to_redis():
    """Sync all local JSON data to Redis"""
    
    # Check if Redis is connected
    redis_conn = get_kv_connection()
    if not redis_conn:
        print("❌ Redis not connected. Please set REDIS_URL environment variable.")
        print("\nExample:")
        print('export REDIS_URL="redis://default:password@host:port"')
        return False
    
    print("✓ Redis connection successful\n")
    
    # Files to sync
    files_to_sync = {
        'audiences': 'database/audiences.json',
        'users': 'database/users.json',
        'blog': 'database/blog.json',
        'settings': 'database/settings.json',
        'categories': 'categories.json'
    }
    
    synced_count = 0
    failed_count = 0
    
    for key, file_path in files_to_sync.items():
        try:
            if not os.path.exists(file_path):
                print(f"⚠️  {file_path} not found, skipping...")
                continue
            
            # Load from file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Write to Redis
            if JSONStore.write(key, data):
                record_count = len(data) if isinstance(data, dict) else "N/A"
                print(f"✓ Synced '{key}': {record_count} records from {file_path}")
                synced_count += 1
            else:
                print(f"❌ Failed to sync '{key}' from {file_path}")
                failed_count += 1
                
        except Exception as e:
            print(f"❌ Error syncing '{key}': {e}")
            failed_count += 1
    
    print(f"\n{'='*50}")
    print(f"Summary: {synced_count} synced, {failed_count} failed")
    print(f"{'='*50}")
    
    return failed_count == 0

def verify_redis_data():
    """Verify data exists in Redis"""
    print("\n\nVerifying Redis data...")
    print(f"{'='*50}\n")
    
    redis_conn = get_kv_connection()
    if not redis_conn:
        print("❌ Redis not connected")
        return
    
    keys_to_check = ['audiences', 'users', 'blog', 'settings', 'categories']
    
    for key in keys_to_check:
        try:
            data = JSONStore.read(key)
            record_count = len(data) if isinstance(data, dict) else 0
            if record_count > 0:
                print(f"✓ '{key}': {record_count} records")
            else:
                print(f"⚠️  '{key}': No data (empty)")
        except Exception as e:
            print(f"❌ Error reading '{key}': {e}")
    
    print(f"\n{'='*50}")

if __name__ == '__main__':
    print("="*50)
    print("  Syncing Local Data to Vercel Redis")
    print("="*50)
    print()
    
    # Sync data
    success = sync_data_to_redis()
    
    # Verify
    if success:
        verify_redis_data()
        print("\n✅ All data synced successfully!")
        print("\nNext steps:")
        print("1. Deploy to Vercel: git push origin main")
        print("2. Test the Audience button on Vercel deployment")
    else:
        print("\n⚠️  Some files failed to sync. Please check errors above.")
