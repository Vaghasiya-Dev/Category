import json
from pathlib import Path
from flask import current_app


class SettingsService:
    """Service to manage app settings stored in JSON."""

    def __init__(self):
        self.db_path = Path(current_app.config['SETTINGS_DB_PATH'])
        self.db_path.parent.mkdir(exist_ok=True)

    def _load(self):
        if not self.db_path.exists():
            return {"theme": "default", "allow_signups": False}
        with open(self.db_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save(self, data):
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_settings(self):
        return self._load()

    def update_settings(self, payload):
        data = self._load()
        data.update(payload)
        self._save(data)
        return data
