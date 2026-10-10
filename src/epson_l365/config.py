# Configuration settings for the Epson L365 maintenance application

# Printer connection details
PRINTER_IP = "192.168.1.100"
DISCORD_WEBHOOK = "URL_DO_WEBHOOKA"
CLEANING_INTERVAL_DAYS = 14
STATE_FILE = "/data/printer_state.json"
SNMP_PAYLOAD_HEX = (
	"303202010004067075626c6963a025020112020100020100301a301806142b"
	"0601040189600102022c0101020163640100000500"
)
CLEANING_PAYLOAD_HEX = ""
CLEANING_PORT = 9100
SNMP_PORT = 161
SOCKET_TIMEOUT_SECONDS = 4

# Maintenance settings

# Logging settings
LOG_FILE = "epson_l365.log"  # Log file name
LOG_LEVEL = "INFO"  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

# Other constants
SUPPORTED_PAPER_SIZES = ["A4", "A5", "Letter", "Legal"]  # Supported paper sizes for printing
