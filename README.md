# Epson L365 idle cleaning

A small daily maintenance script for the Epson EcoTank L365. It reads printer telemetry over SNMP, detects long periods without printing, triggers a light cleaning over raw TCP, and reports confirmed or cancelled cleanings to Discord.

The script runs once and exits. Persistent state is stored in `/data/printer_state.json`, so it can be started by cron, Portainer, or another scheduler.

## Configuration

Set `PRINTER_HOST` in the environment. It is required and can be a hostname or an IP address.

All other settings are optional environment variables. If unset, their defaults from `src/epson_l365/config.py` are used:

- `PRINTER_HOST`: printer hostname or address (required)
- `DISCORD_WEBHOOK`: Discord webhook URL
- `CLEANING_INTERVAL_DAYS`: idle period before scheduling cleaning
- `CLEANING_PAYLOAD_HEX`: raw cleaning command
- `STATE_FILE`, `SNMP_PAYLOAD_HEX`, `CLEANING_PORT`, `SNMP_PORT`
- `SOCKET_TIMEOUT_SECONDS`, `CLEANING_CONFIRMATION_DELAY_SECONDS`
- `CLEANING_RETRY_DELAY_SECONDS`, `CLEANING_MAX_ATTEMPTS`

An empty `DISCORD_WEBHOOK` disables notifications.

The default cleaning command targets Epson L365 firmware and should not be changed unless the printer protocol is known. Cleaning confirmation waits 3 minutes and retries up to two times at 10-minute intervals.

## Local run

Install the only runtime dependency and run one check from the repository root:

```sh
python -m pip install -r requirements.txt
export PRINTER_HOST=printer.local
python -m src.epson_l365.main
```

## Docker

Build and run the one-shot container with Compose:

```sh
docker compose build
docker compose run --rm epson-l365-cleaning
```

Keep `/data` on a persistent volume. The container needs network access to the printer on UDP port `161` and TCP port `9100`.

The included `docker-compose.yml` uses an isolated Docker bridge network. It does not use host networking and does not publish any container ports. Docker forwards the container's outbound traffic through NAT, so the container can reach the printer while remaining isolated from the VM network namespace.

For Portainer, deploy the repository as a Stack using `docker-compose.yml`. Start the service manually for the first test; it exits normally after completing one check. Schedule the service to run once per day with the scheduler available on the Docker host or in Portainer.

In the Stack's environment variables, set `PRINTER_HOST` (required). Add any optional variables you want to override; omitted variables use the defaults from `config.py`.

## Tests

```sh
python -m unittest tests.test_printer -v
```

## License

This project is licensed under the [MIT License](LICENSE).
