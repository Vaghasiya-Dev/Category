import os
import json
import redis
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Redis KV connection with fallback for local development
_kv_instance = None

def get_kv_connection():
    """Get KV connection, with fallback for local development"""
    global _kv_instance
    
    if _kv_instance is not None:
        return _kv_instance
    
    # Try both REDIS_URL and KV_URL for compatibility
    kv_url = os.environ.get('REDIS_URL') or os.environ.get('KV_URL')
    if kv_url:
        # Remove quotes if present
        kv_url = kv_url.strip('"').strip("'")
        try:
            _kv_instance = redis.from_url(kv_url, decode_responses=True, socket_connect_timeout=5)
            # Test connection
            _kv_instance.ping()
            return _kv_instance
        except Exception as e:
            print(f"Warning: Could not connect to Redis: {e}. Using local fallback.")
            _kv_instance = False  # Mark as failed
            return None
    _kv_instance = False  # Mark as not configured
    return None

# Get the connection
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
                # Using Redis KV
                data = kv.get(key)
                if data:
                    # decode_responses=True means data is already a string
                    if isinstance(data, str):
                        return json.loads(data)
                    return data
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
                # Using Redis KV
                kv.set(key, json.dumps(data, ensure_ascii=False))
                return True
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


