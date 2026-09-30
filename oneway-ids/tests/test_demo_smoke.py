"""Opt-in end-to-end check: alerts arrive while the paced FIFO is live.

Run with the repository's normal Nix loader setup, for example:
    .venv/bin/python tests/test_demo_smoke.py
"""
import os
import re
import signal
import select
import subprocess
import sys
import time
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class DemoSmokeTests(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("DIODESENTINEL_DEMO_SMOKE") == "1",
                         "set DIODESENTINEL_DEMO_SMOKE=1 to run the live demo")
    def test_alerts_arrive_during_replay_and_ctrl_c_cleans_up(self):
        proc = subprocess.Popen(
            [os.path.join(ROOT, "demo.sh"), "--speed=20", "--port=18603"],
            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1)
        run_dir = None
        output = []
        deadline = time.monotonic() + 55
        try:
            while time.monotonic() < deadline:
                ready, _, _ = select.select([proc.stdout], [], [], .1)
                line = proc.stdout.readline() if ready else ""
                if line:
                    output.append(line)
                    match = re.search(r"/tmp/diode-sentinel-demo\.[^/\s]+", line)
                    if match:
                        run_dir = match.group(0)
                if run_dir:
                    alert_path = os.path.join(run_dir, "alerts.jsonl")
                    try:
                        with open(alert_path) as fh:
                            alerts = sum(1 for row in fh if row.strip())
                    except OSError:
                        alerts = 0
                    if alerts:
                        self.assertIsNone(proc.poll(), "demo exited before the live alert check")
                        cmdline = subprocess.run(
                            ["pgrep", "-af", re.escape(run_dir)],
                            capture_output=True, text=True, check=False).stdout
                        self.assertIn("run.py --pipe", cmdline)
                        self.assertIn("demo_replay.py", cmdline)
                        break
                if proc.poll() is not None:
                    self.fail("demo exited before a mid-replay alert appeared:\n" +
                              "".join(output))
            else:
                self.fail("timed out waiting for a mid-replay alert:\n" +
                          "".join(output))
        finally:
            if proc.poll() is None:
                proc.send_signal(signal.SIGINT)
            try:
                proc.wait(timeout=8)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=3)
        self.assertIsNotNone(run_dir, "demo did not report its isolated output directory")
        self.assertFalse(os.path.exists(run_dir), "Ctrl-C left temporary demo files behind")
        leftovers = subprocess.run(
            ["pgrep", "-af", re.escape(run_dir)],
            capture_output=True, text=True, check=False).stdout
        self.assertNotIn("run.py --pipe", leftovers)
        self.assertNotIn("demo_replay.py", leftovers)
        dashboard = subprocess.run(
            ["pgrep", "-af", "[d]ashboard.py 18603"],
            capture_output=True, text=True, check=False).stdout
        self.assertEqual(dashboard.strip(), "")
        proc.stdout.close()


if __name__ == "__main__":
    unittest.main()
