import json
import os
from datetime import date


def _default_state():
    return {
        "last_counter": 0,
        "last_activity_date": date.today().isoformat(),
        "cleaning_scheduled": False,
        "notified_offline_interval": False,
        "notified_offline_sched": False,
    }


def load_state(path):
    if not os.path.exists(path):
        return _default_state()
    with open(path, "r", encoding="utf-8") as state_file:
        state = json.load(state_file)
    defaults = _default_state()
    defaults.update(state)
    return defaults


def save_state(path, state):
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    temporary_path = f"{path}.tmp"
    with open(temporary_path, "w", encoding="utf-8") as state_file:
        json.dump(state, state_file, indent=2)
        state_file.write("\n")
    os.replace(temporary_path, path)
