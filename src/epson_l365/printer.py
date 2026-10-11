import socket
import struct

from . import config


def read_telemetry():
    payload = bytes.fromhex(config.SNMP_PAYLOAD_HEX)
    marker = bytes.fromhex("63 64 01 00 00")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(config.SOCKET_TIMEOUT_SECONDS)
        sock.sendto(payload, (config.PRINTER_HOST, config.SNMP_PORT))
        response, _ = sock.recvfrom(4096)

    marker_index = response.find(marker)
    data_start = marker_index + len(marker)
    if marker_index < 0 or len(response) < data_start + 75:
        raise ValueError("SNMP response does not contain complete telemetry")
    data = response[data_start:]
    return {
        "manual_cleanings": data[24],
        "total_pages": struct.unpack_from("<I", data, 37)[0],
    }


def read_counter():
    return read_telemetry()["total_pages"]


def read_cleaning_counter():
    return read_telemetry()["manual_cleanings"]

def trigger_cleaning():
    payload = bytes.fromhex(config.CLEANING_PAYLOAD_HEX)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
            connection.settimeout(5)
            connection.connect((config.PRINTER_HOST, config.CLEANING_PORT))
            connection.sendall(payload)
    except socket.timeout:
        return False
    except ConnectionRefusedError:
        return False
    except OSError:
        return False
    return True

class Printer:
    def __init__(self, connection_details=None):
        self.connection_details = connection_details or {"host": config.PRINTER_HOST}
        self.status = None

    def check_status(self):
        try:
            read_counter()
        except (OSError, ValueError, struct.error):
            self.status = "offline"
        else:
            self.status = "online"
        return self.status

    def send_print_job(self, document):
        if not document:
            raise ValueError("document must not be empty")
        return True

    def perform_maintenance(self):
        return trigger_cleaning()

    def get_status(self):
        return self.status

    def update_status(self, new_status):
        self.status = new_status