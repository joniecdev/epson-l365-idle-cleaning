import struct
from datetime import date

import requests

from . import config
from .printer import read_counter, trigger_cleaning
from .state import load_state, save_state


def notify_discord(message):
    if not config.DISCORD_WEBHOOK or config.DISCORD_WEBHOOK == "URL_DO_WEBHOOKA":
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


def process_once(today=None):
    today = today or date.today()
    state = load_state(config.STATE_FILE)
    last_activity = date.fromisoformat(state["last_activity_date"])

    try:
        current_counter = read_counter()
    except (OSError, ValueError, struct.error):
        if state["cleaning_scheduled"]:
            if not state["notified_offline_sched"]:
                notify_discord(
                    "⚠️ Drukarka jest offline w dniu zaplanowanego czyszczenia. "
                    "Czekam na powrót do sieci."
                )
                state["notified_offline_sched"] = True
        elif (today - last_activity).days >= config.CLEANING_INTERVAL_DAYS - 1:
            if not state["notified_offline_interval"]:
                notify_discord(
                    "⚠️ Minął czas bezruchu, ale drukarka jest wyłączona. "
                    "Włącz ją, abym mógł jutro zaplanować czyszczenie."
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
            notify_discord("🛑 Wykryto nowe wydruki. Anuluję zaplanowane czyszczenie.")
            state["cleaning_scheduled"] = False
    elif state["cleaning_scheduled"]:
        if trigger_cleaning():
            notify_discord("✅ Wykonano zaplanowane, lekkie czyszczenie głowicy.")
            state["cleaning_scheduled"] = False
            state["last_activity_date"] = today.isoformat()
    elif (today - last_activity).days >= config.CLEANING_INTERVAL_DAYS - 1:
        idle_days = (today - last_activity).days
        notify_discord(
            f"⏳ Brak wydruków od {idle_days} dni. Planuję lekkie czyszczenie na jutro."
        )
        state["cleaning_scheduled"] = True

    state["last_counter"] = max(state["last_counter"], current_counter)
    save_state(config.STATE_FILE, state)
    return state


def main():
    process_once()


if __name__ == "__main__":
    main()
