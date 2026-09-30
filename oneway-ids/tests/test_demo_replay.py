"""Behavior checks for the paced FIFO replay adapter."""
import os
import struct
import tempfile
import unittest
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from demo_replay import replay


class DemoReplayTests(unittest.TestCase):
    def test_preserves_capture_and_scales_capture_time_delays(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, destination = (os.path.join(tmp, name)
                                   for name in ("in.pcap", "out.pcap"))
            global_header = (b"\xd4\xc3\xb2\xa1" +
                             struct.pack("<HHIIII", 2, 4, 0, 0, 65535, 1))
            records = [(100, 0, b"first"), (101, 500000, b"second")]
            with open(source, "wb") as fh:
                fh.write(global_header)
                for sec, usec, frame in records:
                    fh.write(struct.pack("<IIII", sec, usec, len(frame), len(frame)))
                    fh.write(frame)

            now = [0.0]
            sleeps = []
            def sleep(delay):
                sleeps.append(delay)
                now[0] += delay
            def clock():
                return now[0]

            self.assertEqual(replay(source, destination, speed=3,
                                    sleep=sleep, clock=clock), 2)
            self.assertEqual(sleeps, [0.5])
            with open(destination, "rb") as got, open(source, "rb") as expected:
                self.assertEqual(got.read(), expected.read())

    def test_rejects_zero_speed(self):
        with self.assertRaisesRegex(ValueError, "greater than zero"):
            replay("unused", "unused", speed=0)


if __name__ == "__main__":
    unittest.main()
