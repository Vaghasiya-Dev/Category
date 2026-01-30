import os
import json
import redis

# Initialize Redis KV connection
kv = redis.from_url(os.environ.get('KV_URL', 'redis://localhost'))

class JSONStore:
    """Store and retrieve JSON data using Vercel KV"""
    
    @staticmethod
    def read(key):
        """Read JSON from KV"""
        try:
            data = kv.get(key)
            if data:
                return json.loads(data)
            return {}
        except Exception as e:
            print(f"Error reading from KV: {e}")
            return {}
    
    @staticmethod
    def write(key, data):
        """Write JSON to KV"""
        try:
            kv.set(key, json.dumps(data))
            return True
        except Exception as e:
            print(f"Error writing to KV: {e}")
            return False
    
    @staticmethod
    def delete(key):
        """Delete data from KV"""
        try:
            kv.delete(key)
            return True
        except Exception as e:
            print(f"Error deleting from KV: {e}")
            return False
