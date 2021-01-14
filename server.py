#!/usr/bin/env python3
import socket
import argparse
import serial
import select
import struct
import sys
import time
import math

parser = argparse.ArgumentParser(
    "Client for sending controller commands to a controller emulator"
)
parser.add_argument("port")
args = parser.parse_args()

STATE_OUT_OF_SYNC = 0
STATE_SYNC_START = 1
STATE_SYNC_1 = 2
STATE_SYNC_2 = 3
STATE_SYNC_OK = 4

NO_INPUT = 0x0000000000000000

# Commands to send to MCU
COMMAND_NOP = 0x00
COMMAND_SYNC_1 = 0x33
COMMAND_SYNC_2 = 0xCC
COMMAND_SYNC_START = 0xFF

# Responses from MCU
RESP_USB_ACK = 0x90
RESP_UPDATE_ACK = 0x91
RESP_UPDATE_NACK = 0x92
RESP_SYNC_START = 0xFF
RESP_SYNC_1 = 0xCC
RESP_SYNC_OK = 0x33


# Precision wait
def p_wait(waitTime):
    t0 = time.perf_counter()
    t1 = t0
    while t1 - t0 < waitTime:
        t1 = time.perf_counter()


# Wait for data to be available on the serial port
def wait_for_data(timeout=1.0, sleepTime=0.1):
    t0 = time.perf_counter()
    t1 = t0
    inWaiting = ser.in_waiting
    while (t1 - t0 < sleepTime) or (inWaiting == 0):
        time.sleep(sleepTime)
        inWaiting = ser.in_waiting
        t1 = time.perf_counter()


# Read X bytes from the serial port (returns list)
def read_bytes(size):
    bytes_in = ser.read(size)
    return list(bytes_in)


# Read 1 byte from the serial port (returns int)
def read_byte():
    bytes_in = read_bytes(1)
    if len(bytes_in) != 0:
        byte_in = bytes_in[0]
    else:
        byte_in = 0
    return byte_in


# Discard all incoming bytes and read the last (latest) (returns int)
def read_byte_latest():
    inWaiting = ser.in_waiting
    if inWaiting == 0:
        inWaiting = 1
    bytes_in = read_bytes(inWaiting)
    if len(bytes_in) != 0:
        byte_in = bytes_in[0]
    else:
        byte_in = 0
    return byte_in


# Write bytes to the serial port
def write_bytes(bytes_out):
    ser.write(bytearray(bytes_out))
    return


# Write byte to the serial port
def write_byte(byte_out):
    write_bytes([byte_out])
    return


# Compute CRC8
# https://www.microchip.com/webdoc/AVRLibcReferenceManual/group__util__crc_1gab27eaaef6d7fd096bd7d57bf3f9ba083.html
def crc8_ccitt(old_crc, new_data):
    data = old_crc ^ new_data

    for i in range(8):
        if (data & 0x80) != 0:
            data = data << 1
            data = data ^ 0x07
        else:
            data = data << 1
        data = data & 0xFF
    return data


# Send a raw packet and wait for a response (CRC will be added automatically)
def send_packet(packet=[0x00, 0x00, 0x08, 0x80, 0x80, 0x80, 0x80, 0x00], debug=False):
    if not debug:
        bytes_out = []
        bytes_out.extend(packet)

        # Compute CRC
        crc = 0
        for d in packet:
            crc = crc8_ccitt(crc, d)
        bytes_out.append(crc)
        write_bytes(bytes_out)
        # print(bytes_out)

        # Wait for USB ACK or UPDATE NACK
        byte_in = read_byte()
        commandSuccess = byte_in == RESP_USB_ACK
    else:
        commandSuccess = True
    return commandSuccess


# Send a formatted controller command to the MCU
def send_cmd(command=NO_INPUT):
    if isinstance(command, int):
        # Send empty packet if resetting input
        return send_packet()
    commandSuccess = send_packet(command)
    return commandSuccess


# Force MCU to sync
def force_sync():
    # Send 9x 0xFF's to fully flush out buffer on device
    # Device will send back 0xFF (RESP_SYNC_START) when it is ready to sync
    write_bytes([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])

    # Wait for serial data and read the last byte sent
    wait_for_data()
    byte_in = read_byte_latest()

    # Begin sync...
    inSync = False
    if byte_in == RESP_SYNC_START:
        write_byte(COMMAND_SYNC_1)
        byte_in = read_byte()
        if byte_in == RESP_SYNC_1:
            write_byte(COMMAND_SYNC_2)
            byte_in = read_byte()
            if byte_in == RESP_SYNC_OK:
                inSync = True
    return inSync


# Start MCU syncing process
def sync():
    inSync = False

    # Try sending a packet
    inSync = send_packet()
    if not inSync:
        # Not in sync: force resync and send a packet
        inSync = force_sync()
        if inSync:
            inSync = send_packet()
    return inSync


# -------------------------------------------------------------------------


host = "127.0.0.1"
port = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet  # UDP
sock.bind((host, port))

ser = serial.Serial(port=args.port, baudrate=19200, timeout=1)

# Attempt to sync with the MCU
if not sync():
    print("Could not sync!")

p_wait(0.05)

if not send_cmd():
    print("Packet Error!")

while True:
    data, addr = sock.recvfrom(1024)
    if data:
        send_cmd([byte for byte in data])
        p_wait(0.1)
        send_cmd()
        p_wait(0.001)


ser.close
