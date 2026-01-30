import os
import json
import redis
from pathlib import Path

# Initialize Redis KV connection with fallback for local development
def get_kv_connection():
    """Get KV connection, with fallback for local development"""
    kv_url = os.environ.get('KV_URL')
    if kv_url:
        try:
            return redis.from_url(kv_url)
        except Exception as e:
            print(f"Warning: Could not connect to Vercel KV: {e}. Using local fallback.")
            return None
    return None

kv = get_kv_connection()

# Map of KV keys to local JSON file paths
JSON_FILE_MAP = {
    'users': 'database/users.json',
    'audiences': 'database/audiences.json',
    'categories': 'categories.json',
    'blog': 'database/blog.json',
    'settings': 'database/settings.json'
}

class JSONStore:
    """Store and retrieve JSON data using Vercel KV or local JSON files"""
    
    # Base directory (backend folder)
    BASE_DIR = Path(__file__).parent.parent
    
    @staticmethod
    def _get_file_path(key):
        """Get file path for a given key"""
        if key in JSON_FILE_MAP:
            return JSONStore.BASE_DIR / JSON_FILE_MAP[key]
        return None
    
    @staticmethod
    def _load_from_file(key):
        """Load data from local JSON file"""
        file_path = JSONStore._get_file_path(key)
        if file_path and file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    return json.loads(content) if content else {}
            except (json.JSONDecodeError, OSError) as e:
                print(f"Error loading {key} from file: {e}")
                return {}
        return {}
    
    @staticmethod
    def _save_to_file(key, data):
        """Save data to local JSON file"""
        file_path = JSONStore._get_file_path(key)
        if file_path:
            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return True
            except Exception as e:
                print(f"Error saving {key} to file: {e}")
                return False
        return False
    
    @staticmethod
    def read(key):
        """Read JSON from KV or local file"""
        try:
            if kv:
                # Using Vercel KV
                data = kv.get(key)
                if data:
                    return json.loads(data)
                return {}
            else:
                # Using local JSON files
                return JSONStore._load_from_file(key)
        except Exception as e:
            print(f"Error reading {key}: {e}")
            return {}
    
    @staticmethod
    def write(key, data):
        """Write JSON to KV or local file"""
        try:
            if kv:
                # Using Vercel KV
                kv.set(key, json.dumps(data))
            else:
                # Using local JSON files
                JSONStore._save_to_file(key, data)
            return True
        except Exception as e:
            print(f"Error writing {key}: {e}")
            return False
    
    @staticmethod
    def delete(key):
        """Delete data from KV or local file"""
        try:
            if kv:
                kv.delete(key)
            else:
                # For local files, just write empty dict
                JSONStore._save_to_file(key, {})
            return True
        except Exception as e:
            print(f"Error deleting {key}: {e}")
            return False


