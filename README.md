# Epson L365 idle cleaning

A small daily maintenance script for the Epson EcoTank L365. It reads printer telemetry over SNMP, detects long periods without printing, triggers a light cleaning over raw TCP, and reports confirmed or cancelled cleanings to Discord.

The script runs once and exits. Persistent state is stored in `/data/printer_state.json`, so it can be started by cron, Portainer, or another scheduler.

## Configuration

Edit `src/epson_l365/config.py`:

- `PRINTER_IP`: printer address
- `DISCORD_WEBHOOK`: Discord webhook URL
- `CLEANING_INTERVAL_DAYS`: idle period before scheduling cleaning
- `CLEANING_PAYLOAD_HEX`: raw cleaning command

The default cleaning command targets Epson L365 firmware and should not be changed unless the printer protocol is known. Cleaning confirmation waits 3 minutes and retries up to two times at 10-minute intervals.

## Local run

Install the only runtime dependency and run one check from the repository root:

```sh
python -m pip install -r requirements.txt
python -m src.epson_l365.main
```

## Docker

Build and run the one-shot container:

```sh
docker build -t epson-l365-cleaning .
docker volume create epson-l365-data
docker run --rm \
  -v epson-l365-data:/data \
  epson-l365-cleaning
```

Keep `/data` on a persistent volume. The container needs network access to the printer on UDP port `161` and TCP port `9100`.

For Portainer, deploy the repository as a Stack or build the image from the included `Dockerfile`. Schedule the container to run once per day; it exits normally after completing one check.

## Tests

```sh
python -m unittest tests.test_printer -v
```

## License

This project is licensed under the [MIT License](LICENSE).
