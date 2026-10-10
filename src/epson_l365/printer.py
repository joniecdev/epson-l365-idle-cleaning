import socket
import struct

from . import config

def read_counter():
    payload = bytes.fromhex(config.SNMP_PAYLOAD_HEX)
    marker = bytes.fromhex("63 64 01 00 00")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(config.SOCKET_TIMEOUT_SECONDS)
        sock.sendto(payload, (config.PRINTER_IP, config.SNMP_PORT))
        response, _ = sock.recvfrom(4096)

    marker_index = response.find(marker)
    counter_start = marker_index + len(marker)
    if marker_index < 0 or len(response) < counter_start + 4:
        raise ValueError("SNMP response does not contain a page counter")
    return struct.unpack_from("<I", response, counter_start)[0]

def trigger_cleaning():
    if not config.CLEANING_PAYLOAD_HEX:
        return True
    payload = bytes.fromhex(config.CLEANING_PAYLOAD_HEX)
    with socket.create_connection(
        (config.PRINTER_IP, config.CLEANING_PORT),
        timeout=config.SOCKET_TIMEOUT_SECONDS,
    ) as connection:
        connection.sendall(payload)
    return True

class Printer:
    def __init__(self, connection_details=None):
        self.connection_details = connection_details or {"host": config.PRINTER_IP}
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