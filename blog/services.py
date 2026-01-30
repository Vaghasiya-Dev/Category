import json
from flask import current_app
from database.kv_store import JSONStore


class BlogService:
    """Service to manage blog content using Vercel KV storage."""

    def __init__(self):
        self.kv_key = 'blog'

    def _load(self):
        """Load blog data from KV storage"""
        data = JSONStore.read(self.kv_key)
        if not data:
            return {"title": "", "content": ""}
        return data

    def _save(self, data):
        """Save blog data to KV storage"""
        JSONStore.write(self.kv_key, data)

    def get_blog(self):
        return self._load()

    def update_blog(self, payload):
        data = self._load()
        data.update({
            "title": payload.get("title", data.get("title", "")),
            "content": payload.get("content", data.get("content", ""))
        })
        self._save(data)
        return data
