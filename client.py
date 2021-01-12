#!/usr/bin/env python3
import socket
import json

BUTTON_NONE = 0x00
BUTTON_Y = 0x01
BUTTON_B = 0x02
BUTTON_A = 0x04
BUTTON_X = 0x08
BUTTON_L = 0x10
BUTTON_R = 0x20
BUTTON_ZL = 0x40
BUTTON_ZR = 0x80
BUTTON_MINUS = 0x100
BUTTON_PLUS = 0x200
BUTTON_LCLICK = 0x400
BUTTON_RCLICK = 0x800
BUTTON_HOME = 0x1000
BUTTON_CAPTURE = 0x2000

DPAD_UP = 0x00
DPAD_UP_RIGHT = 0x01
DPAD_RIGHT = 0x02
DPAD_DOWN_RIGHT = 0x03
DPAD_DOWN = 0x04
DPAD_DOWN_LEFT = 0x05
DPAD_LEFT = 0x06
DPAD_UP_LEFT = 0x07
DPAD_CENTER = 0x08

STICK_MIN = -1.0
STICK_CENTER = 0.0
STICK_MAX = 1.0

# left stick - "move [direction]"
# right stick - "look [direction]"

config = None

with open("./config.json") as f:
    config = json.load(f)


class Packet:
    def __init__(self):
        self.buttons = set()
        self.dpad = DPAD_CENTER
        self.lx = STICK_CENTER
        self.ly = STICK_CENTER
        self.rx = STICK_CENTER
        self.ry = STICK_CENTER
        self.vendorspec = b"\x00"

    @staticmethod
    def f2b(val):
        return int((val + 1.0) / 2.0 * 255).to_bytes(1, byteorder="big")

    def press_button(self, button):
        self.buttons.add(button)
        return self

    def press_dpad(self, dpad_press):
        self.dpad = dpad_press
        return self

    def move_left_stick(self, x, y):
        self.lx = x
        self.ly = -y
        return self

    def move_right_stick(self, x, y):
        self.rx = x
        self.ry = -y
        return self

    def generate_bytes(self):
        return (
            sum(self.buttons).to_bytes(2, byteorder="big")
            + self.dpad.to_bytes(1, byteorder="big")
            + Packet.f2b(self.lx)
            + Packet.f2b(self.ly)
            + Packet.f2b(self.rx)
            + Packet.f2b(self.ry)
            + self.vendorspec
        )


# host = "192.168.86.21"
host = "127.0.0.1"
port = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

default_packet = Packet()

while True:
    message = input("Please enter a command: ").encode()
    if len(message) > 0 & (message in config):
        packet = Packet()
        message = message.decode().upper()
        exec(config[message])
        steve = packet.generate_bytes()
        sock.sendto(steve, (host, port))

# twitch chat > client.py > config.json > client.py > server.py > serial > arduino > $$$