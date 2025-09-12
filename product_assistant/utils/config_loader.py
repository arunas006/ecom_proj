from pathlib import Path
import yaml
import os

def _root_path() -> Path:
    return Path(__file__).resolve().parents[1]

def load_config(config_path: str | None = None) -> dict:
    
    env_path=os.getenv("CONFIG_PATH") or config_path or str(_root_path() / "config/config.yaml")

    path=Path(env_path)
    if path.is_absolute():
        path=_root_path() / path
    
    if not path.exists():
        raise FileNotFoundError(f"Config file not found at {path}")

    with open(path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file) or {}

    return config

