"""Small local discovery helper for the MB-FB50E511 cooker."""

from __future__ import annotations

import logging
import select
import socket
import time
from typing import Any

from .const import CONF_DEVICE_ID, CONF_IP, CONF_SN, CONF_SN8, sn8_from_sn
from .midea_lib.security import LocalSecurity

_LOGGER = logging.getLogger(__name__)

DISCOVERY_PORTS = (6445, 20086)
DISCOVERY_TIMEOUT = 8.0
DISCOVERY_MESSAGE = bytes.fromhex(
    "5a5a011148009200000000000000000000000000000000000000000000000000"
    "00000000000000007f75bd6b3e4f8b762e849c6e578d6590036e9d4342a50f1"
    "f569eb8ec918e92e5"
)


def discover_device(
    ip_address: str, timeout: float = DISCOVERY_TIMEOUT
) -> dict[str, Any]:
    """Discover one Midea device by IP and return local protocol metadata."""
    addresses = _discovery_addresses(ip_address)
    security = LocalSecurity()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setblocking(False)

    try:
        for address in addresses:
            for port in DISCOVERY_PORTS:
                sock.sendto(DISCOVERY_MESSAGE, (address, port))

        deadline = time.time() + timeout
        while time.time() < deadline:
            ready, _, _ = select.select([sock], [], [], 0.2)
            if not ready:
                continue

            try:
                data, addr = sock.recvfrom(1024)
            except ConnectionResetError:
                continue

            if addr[0] != ip_address:
                continue

            info = _parse_response(data, addr[0], security)
            if info:
                return info
    finally:
        sock.close()

    return {}


def _discovery_addresses(ip_address: str) -> list[str]:
    return [ip_address]


def _parse_response(
    data: bytes, ip_address: str, security: LocalSecurity
) -> dict[str, Any] | None:
    if data[:2].hex() == "8370" and data[8:10].hex() == "5a5a":
        return _parse_v2_v3_response(data[8:-16], ip_address, security)
    if data[:2].hex() != "5a5a":
        return None
    if data[2:4].hex() == "0110":
        return _parse_0110_response(data, ip_address)
    return _parse_v2_v3_response(data, ip_address, security)


def _parse_v2_v3_response(
    inner_data: bytes, ip_address: str, security: LocalSecurity
) -> dict[str, Any] | None:
    try:
        device_id = int.from_bytes(inner_data[20:26], "little")
        encrypted = inner_data[40:-16]
        if len(encrypted) < 16:
            return None

        reply = security.aes_decrypt(encrypted)
        if len(reply) < 41:
            return None

        sn = bytes(reply[8:40]).decode("utf-8", errors="ignore").rstrip("\x00")
        return {
            CONF_IP: ip_address,
            CONF_DEVICE_ID: device_id,
            CONF_SN: sn,
            CONF_SN8: sn8_from_sn(sn),
        }
    except Exception as err:
        _LOGGER.debug("Failed to parse Midea discovery response: %s", err)
        return None


def _parse_0110_response(data: bytes, ip_address: str) -> dict[str, Any] | None:
    if len(data) < 120:
        return None

    device_id = int.from_bytes(data[16:22], "little")
    return {
        CONF_IP: ip_address,
        CONF_DEVICE_ID: device_id,
    }
