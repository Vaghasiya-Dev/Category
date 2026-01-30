import json
from flask import current_app
from database.kv_store import JSONStore


class SettingsService:
    """Service to manage app settings using Vercel KV storage."""

    def __init__(self):
        self.kv_key = 'settings'

    def _load(self):
        """Load settings from KV storage"""
        data = JSONStore.read(self.kv_key)
        if not data:
            return {"theme": "default", "allow_signups": False}
        return data

    def _save(self, data):
        """Save settings to KV storage"""
        JSONStore.write(self.kv_key, data)

    def get_settings(self):
        return self._load()

    def update_settings(self, payload):
        data = self._load()
        data.update(payload)
        self._save(data)
        return data
