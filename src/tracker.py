import json
import os

STATE_FILE = "data/processed/processed_files.json"


def load_state():
    if not os.path.exists(STATE_FILE):
        return set()
    with open(STATE_FILE, "r") as f:
        return set(json.load(f))


def save_state(processed_set):
    os.makedirs("data/processed", exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(list(processed_set), f)
