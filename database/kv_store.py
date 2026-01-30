import os
import json
import redis

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

class JSONStore:
    """Store and retrieve JSON data using Vercel KV or local fallback"""
    
    # Local fallback storage for development
    _local_store = {}
    
    @staticmethod
    def read(key):
        """Read JSON from KV or local storage"""
        try:
            if kv:
                data = kv.get(key)
                if data:
                    return json.loads(data)
            else:
                # Local fallback for development
                if key in JSONStore._local_store:
                    return JSONStore._local_store[key]
            return {}
        except Exception as e:
            print(f"Error reading from KV: {e}")
            return {}
    
    @staticmethod
    def write(key, data):
        """Write JSON to KV or local storage"""
        try:
            if kv:
                kv.set(key, json.dumps(data))
            else:
                # Local fallback for development
                JSONStore._local_store[key] = data
            return True
        except Exception as e:
            print(f"Error writing to KV: {e}")
            return False
    
    @staticmethod
    def delete(key):
        """Delete data from KV or local storage"""
        try:
            if kv:
                kv.delete(key)
            else:
                # Local fallback for development
                if key in JSONStore._local_store:
                    del JSONStore._local_store[key]
            return True
        except Exception as e:
            print(f"Error deleting from KV: {e}")
            return False

