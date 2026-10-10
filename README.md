# Epson L365 idle cleaning

Mały skrypt uruchamiany raz dziennie. Odczytuje licznik stron drukarki Epson L365, zapisuje stan w `/data/printer_state.json` i wysyła powiadomienia przez Discord.

## Konfiguracja

Ustaw te wartości w [config.py](src/epson_l365/config.py):

- `PRINTER_IP`
- `DISCORD_WEBHOOK`
- `CLEANING_PAYLOAD_HEX` (puste oznacza tryb testowy)

## Uruchomienie lokalne

```powershell
$env:PYTHONPATH = "src"
python -m epson_l365.main
```

Polecenie wykonuje dokładnie jedno sprawdzenie. Wywołuj je codziennie przez cron, Harmonogram zadań albo Docker.

## Docker

```powershell
docker build -t epson-l365-cleaning .
docker run --rm -v epson-l365-data:/data epson-l365-cleaning
```

Wolumen `/data` musi być stały, ponieważ zawiera historię licznika i zaplanowanego czyszczenia.

## Testy

```powershell
python -m pytest
```

Kod wykonawczy znajduje się w `src/epson_l365`. Pozostałe moduły projektu zachowują wcześniejsze API i nie są potrzebne do codziennego uruchamiania.
