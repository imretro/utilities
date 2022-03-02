#!/usr/bin/env python3
"""
Removes the palette from an imretro file.
"""

from argparse import ArgumentParser, FileType
import math
import sys

# NOTE Maps pixel mode to number of colors
COLOR_COUNT = {
    0b00: 2,
    0b01: 4,
    0b10: 256,
}

CHANNEL_COUNT = {
    0b00: 1,
    0b01: 3,
    0b10: 4,
}

parser = ArgumentParser(description="Remove the palette from an imretro file.")
parser.add_argument(
    "infile",
    metavar="IN",
    type=FileType("rb"),
    default=sys.stdin,
    help="The source file that contains a palette",
)
parser.add_argument(
    "outfile",
    metavar="OUT",
    type=FileType("wb"),
    default=sys.stdout,
    help="Where the file without a palette should be written",
)
args = parser.parse_args()

with args.infile as source:
    with args.outfile as dest:
        dest.write(source.read(7))
        mode_byte = source.read(1)
        mode = int.from_bytes(mode_byte, "little")
        pixel_mode = mode >> 6
        color_count = COLOR_COUNT[pixel_mode]
        has_palette = (mode & 0b00100000) != 0
        channel_mode = (mode >> 1) & 0b11
        channel_count = CHANNEL_COUNT[channel_mode]
        channel_size = 2 if mode & 1 == 0 else 8

        dest.write(bytes([mode & 0b11000000]))

        dest.write(source.read(3))

        if has_palette:
            # NOTE unit is bytes
            color_size = (channel_size / 8) * channel_count
            palette_size = math.ceil(color_size * color_count)
            source.read(palette_size)
        else:
            sys.stderr.write("No palette to remove\n")
        dest.write(source.read())
