import struct
import time
from datetime import date

import requests

from . import config
from .printer import read_telemetry, trigger_cleaning
from .state import load_state, save_state


def notify_discord(message):
    if not config.DISCORD_WEBHOOK or config.DISCORD_WEBHOOK == "YOUR_DISCORD_WEBHOOK_URL":
        return False
    try:
        response = requests.post(
            config.DISCORD_WEBHOOK,
            json={"content": message},
            timeout=config.SOCKET_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException:
        return False
    return True


def verify_cleaning(page_counter, cleaning_counter):
    for attempt in range(config.CLEANING_MAX_ATTEMPTS):
        if attempt:
            time.sleep(config.CLEANING_RETRY_DELAY_SECONDS)
        trigger_cleaning()
        time.sleep(config.CLEANING_CONFIRMATION_DELAY_SECONDS)
        try:
            telemetry = read_telemetry()
        except (OSError, ValueError, struct.error):
            continue

        if telemetry["total_pages"] > page_counter:
            return "cancelled", telemetry["total_pages"]
        if telemetry["manual_cleanings"] > cleaning_counter:
            return "confirmed", telemetry["total_pages"]
    return "unconfirmed", page_counter


def process_once(today=None):
    today = today or date.today()
    state = load_state(config.STATE_FILE)
    last_activity = date.fromisoformat(state["last_activity_date"])

    try:
        telemetry = read_telemetry()
        current_counter = telemetry["total_pages"]
    except (OSError, ValueError, struct.error):
        if state["cleaning_scheduled"]:
            if not state["notified_offline_sched"]:
                notify_discord(
                    "⚠️ The printer is offline on the scheduled cleaning day. "
                    "Waiting for it to come back online."
                )
                state["notified_offline_sched"] = True
        elif (today - last_activity).days >= config.CLEANING_INTERVAL_DAYS - 1:
            if not state["notified_offline_interval"]:
                notify_discord(
                    "⚠️ The idle period has passed, but the printer is offline. "
                    "Turn it on so cleaning can be scheduled."
                )
                state["notified_offline_interval"] = True
        save_state(config.STATE_FILE, state)
        return state

    state["notified_offline_interval"] = False
    state["notified_offline_sched"] = False
    if current_counter > state["last_counter"]:
        state["last_counter"] = current_counter
        state["last_activity_date"] = today.isoformat()
        if state["cleaning_scheduled"]:
            notify_discord("🛑 New print jobs detected. Cancelling scheduled cleaning.")
            state["cleaning_scheduled"] = False
    elif state["cleaning_scheduled"]:
        cleaning_status, verified_counter = verify_cleaning(
            current_counter,
            telemetry["manual_cleanings"],
        )
        if cleaning_status == "confirmed":
            notify_discord("✅ Scheduled light printhead cleaning completed.")
            state["cleaning_scheduled"] = False
            state["last_activity_date"] = today.isoformat()
        elif cleaning_status == "cancelled":
            notify_discord("🛑 New print jobs detected. Cancelling scheduled cleaning.")
            state["cleaning_scheduled"] = False
            state["last_counter"] = verified_counter
            state["last_activity_date"] = today.isoformat()
    elif (today - last_activity).days >= config.CLEANING_INTERVAL_DAYS - 1:
        state["cleaning_scheduled"] = True

    state["last_counter"] = max(state["last_counter"], current_counter)
    save_state(config.STATE_FILE, state)
    return state


def main():
    process_once()


if __name__ == "__main__":
    main()
