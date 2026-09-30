#!/usr/bin/env python3
"""Write a classic pcap to a FIFO at its capture-time rate.

The demo uses this small adapter to feed run.py's normal --pipe live driver.
It preserves packet bytes and capture timestamps; --speed scales only the
wall-clock delay between records.
"""
import argparse
import struct
import sys
import time


def replay(source, destination, speed=10.0, sleep=time.sleep, clock=time.monotonic):
    """Copy classic pcap records with inter-packet delays divided by speed."""
    if speed <= 0:
        raise ValueError("speed must be greater than zero")
    with open(source, "rb") as src, open(destination, "wb", buffering=0) as dst:
        global_header = src.read(24)
        if len(global_header) != 24:
            raise ValueError("input is not a complete classic pcap")
        magic = global_header[:4]
        formats = {b"\xd4\xc3\xb2\xa1": ("<", 1e6),
                   b"\xa1\xb2\xc3\xd4": (">", 1e6),
                   b"\x4d\x3c\xb2\xa1": ("<", 1e9),
                   b"\xa1\xb2\x3c\x4d": (">", 1e9)}
        if magic not in formats:
            raise ValueError("input must be classic pcap (pcapng is unsupported)")
        endian, fraction_divisor = formats[magic]
        dst.write(global_header)
        previous = None
        deadline = clock()
        count = 0
        while True:
            header = src.read(16)
            if not header:
                break
            if len(header) != 16:
                raise ValueError("truncated pcap record header")
            sec, fraction, captured, original = struct.unpack(endian + "IIII", header)
            frame = src.read(captured)
            if len(frame) != captured:
                raise ValueError("truncated pcap packet")
            timestamp = sec + fraction / fraction_divisor
            if previous is not None:
                deadline += max(0.0, timestamp - previous) / speed
                delay = deadline - clock()
                if delay > 0:
                    sleep(delay)
            dst.write(header)
            dst.write(frame)
            previous = timestamp
            count += 1
    return count


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture")
    parser.add_argument("fifo")
    parser.add_argument("--speed", type=float, default=10.0,
                        help="simulated seconds per wall second (default 10)")
    args = parser.parse_args(argv)
    try:
        count = replay(args.capture, args.fifo, args.speed)
    except (OSError, ValueError) as exc:
        print(f"demo replay: {exc}", file=sys.stderr)
        return 2
    print(f"demo replay: streamed {count} packets at {args.speed:g}x", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
