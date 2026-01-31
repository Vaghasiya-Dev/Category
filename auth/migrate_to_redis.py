import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from database.kv_store import JSON_FILE_MAP, get_kv_connection


def load_env(base_dir: Path) -> None:
    """Load environment variables from .env if present."""
    env_path = base_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)


def migrate_json_to_redis(flush: bool = False) -> None:
    """Migrate all JSON files defined in JSON_FILE_MAP into Redis."""
    base_dir = Path(__file__).parent.parent
    load_env(base_dir)

    kv = get_kv_connection()
    if not kv:
        print("Redis connection not available. Set KV_URL or REDIS_URL.")
        return

    if flush:
        kv.flushdb()
        print("✓ Redis database flushed")

    for key, rel_path in JSON_FILE_MAP.items():
        file_path = base_dir / rel_path
        if not file_path.exists():
            print(f"- Skipping {key}: {file_path} not found")
            continue

        try:
            content = file_path.read_text(encoding="utf-8").strip()
            data = json.loads(content) if content else {}
            kv.set(key, json.dumps(data, ensure_ascii=False))
            print(f"✓ Migrated {key} from {rel_path}")
        except Exception as exc:
            print(f"✗ Failed to migrate {key}: {exc}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate JSON data to Redis")
    parser.add_argument("--flush", action="store_true", help="Flush Redis before migration")
    args = parser.parse_args()

    migrate_json_to_redis(flush=args.flush)
