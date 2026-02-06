#!/usr/bin/env python3

import socket
import sys
import time

HOST = "192.168.1.15"
PORT = 5000
TIMEOUT = 1.0


def send_cmd(cmd: bytes, expect_reply=True) -> bytes:
    s = socket.create_connection((HOST, PORT), timeout=TIMEOUT)
    s.settimeout(TIMEOUT)
    s.sendall(cmd)

    if not expect_reply:
        s.close()
        return b""

    buf = bytearray()
    end = time.time() + TIMEOUT
    while time.time() < end:
        try:
            chunk = s.recv(64)
            if not chunk:
                break
            buf += chunk
            if len(buf) >= 6:  # full TESmart reply
                break
        except socket.timeout:
            break

    s.close()
    return bytes(buf)


def get_active():
    # AA BB 03 10 00 EE  -> read active input
    cmd = bytes([0xAA, 0xBB, 0x03, 0x10, 0x00, 0xEE])
    rx = send_cmd(cmd)

    if len(rx) < 6 or rx[:4] != bytes([0xAA, 0xBB, 0x03, 0x11]):
        print("Unexpected response:", rx.hex(" "))
        sys.exit(1)

    active_zero_based = rx[4]
    print(active_zero_based + 1)


def set_active(n: int):
    if n < 1 or n > 255:
        print("Input must be >= 1")
        sys.exit(1)

    # AA BB 03 01 XX EE  -> switch to input XX
    cmd = bytes([0xAA, 0xBB, 0x03, 0x01, n, 0xEE])
    send_cmd(cmd, expect_reply=False)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        get_active()
    elif len(sys.argv) == 2:
        set_active(int(sys.argv[1]))
    else:
        print(f"Usage: {sys.argv[0]} [input_number]")
        sys.exit(1)
