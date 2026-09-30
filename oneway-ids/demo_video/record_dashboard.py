#!/usr/bin/env python3
"""
Record a cursor-driven tour of the live Diode Sentinel dashboard.

What this produces
------------------
A WebM (and, if ffmpeg is available, an MP4) of the *real* dashboard being
operated: the pointer travels, filters get clicked, an alert row opens its
evidence panel. The pointer is synthetic -- Playwright's screencast API
(`show_actions(cursor="pointer")`) draws a cursor that animates from the
previous action point to the next. There is no physical mouse in a headless
browser, and there is no recorded human.

Why a browser recorder at all
-----------------------------
The dashboard is a stdlib HTTP server with no client-side build step, so
Playwright can drive it as-is. Driving it means the demo shows the shipping
code path (dashboard.py -> /api/alerts -> app.js), not a mockup. The
alternative -- screenshotting a still page and panning over it -- cannot show
a click actually filtering the queue.

Honesty constraints (AGENTS.md / HANDOFF.md)
--------------------------------------------
Every step below targets a real element served from a real alert file, and the
chapter text only restates wording the dashboard itself uses. It must not
assert anything this repo calls false: the capture is a synthetic replay,
counts are alert records rather than incidents, and a one-way feed cannot
confirm delivery, response or application outcome. Do not add a chapter that
claims "zero false positives", presents the ML tier as robust, or promises
MITRE technique IDs.

Usage
-----
    # run inside the dev shell, which provides playwright + ffmpeg + chromium
    nix develop --command demo-python demo_video/record_dashboard.py

Options:
    --alerts PATH   alert JSONL to serve (default: the ML regression fixture)
    --port N        dashboard port (default 8701, deliberately off 8600)
    --out PATH      where to write the WebM
    --size WxH      recording size (default 1920x1080)
    --no-mp4        keep only the WebM
"""
from __future__ import annotations

import argparse
import os
import pathlib
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

PROJECT_DIR = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_ALERTS = PROJECT_DIR / ".regression" / "alerts_ml.reference.jsonl"


# --------------------------------------------------------------------------
# choreography helpers
# --------------------------------------------------------------------------
def glide(page, selector: str, *, steps: int = 26, settle_ms: int = 260) -> bool:
    """Slide the pointer to an element's centre before anything else happens.

    Playwright's cursor decoration animates *between action points*, but it
    only appears when an action runs. An explicit mouse.move in steps is what
    gives the recording a visible travel across the screen, which reads as
    "someone operating the UI" rather than "frames appearing". Returns False
    if the element is absent, so a changed dashboard degrades to a shorter
    tour instead of a crashed recording.
    """
    try:
        loc = page.locator(selector).first
        loc.wait_for(state="visible", timeout=4000)
        loc.scroll_into_view_if_needed(timeout=4000)
        box = loc.bounding_box()
    except Exception:
        print(f"  skip (not found): {selector}")
        return False
    if box:
        page.mouse.move(
            box["x"] + box["width"] / 2,
            box["y"] + box["height"] / 2,
            steps=steps,
        )
        page.wait_for_timeout(settle_ms)
    return True


def open_browsable(page) -> None:
    """Wait until the dashboard has actually fetched data.

    Recording before the first /api/alerts response would capture an empty
    queue and an "connecting" pill, which misrepresents the product.
    """
    page.wait_for_selector("#alert-rows tr", timeout=15000)
    page.wait_for_timeout(600)


# --------------------------------------------------------------------------
# server lifecycle
# --------------------------------------------------------------------------
def wait_for_server(port: int, timeout: float = 25.0) -> None:
    deadline = time.time() + timeout
    url = f"http://127.0.0.1:{port}/api/stats"
    last: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status == 200:
                    return
        except (urllib.error.URLError, OSError) as exc:  # not up yet
            last = exc
            time.sleep(0.35)
    raise RuntimeError(f"dashboard never became ready at {url}: {last}")


def dashboard_python() -> str:
    """Interpreter used to run the dashboard itself.

    The dashboard is stdlib-only, but it imports core.config, and the repo's
    convention is that everything runs under .venv. Fall back to the current
    interpreter for a bare checkout with no synced venv.
    """
    venv = PROJECT_DIR / ".venv" / "bin" / "python"
    return str(venv) if venv.exists() else sys.executable


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--alerts", default=str(DEFAULT_ALERTS))
    ap.add_argument("--port", type=int, default=8701)
    ap.add_argument("--out", default=str(PROJECT_DIR / "demo_video" / "out" / "dashboard_tour.webm"))
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--no-mp4", action="store_true")
    args = ap.parse_args()

    alerts = pathlib.Path(args.alerts)
    if not alerts.exists():
        print(f"alert file not found: {alerts}", file=sys.stderr)
        return 2
    width, height = (int(v) for v in args.size.lower().split("x"))

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "playwright is not importable. Run this under the dev shell:\n"
            "  nix develop --command demo-python demo_video/record_dashboard.py",
            file=sys.stderr,
        )
        return 3

    env = dict(os.environ, DIODESENTINEL_ALERTS_PATH=str(alerts))
    srv = subprocess.Popen(
        [dashboard_python(), str(PROJECT_DIR / "dashboard.py"), str(args.port)],
        cwd=str(PROJECT_DIR),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    try:
        wait_for_server(args.port)
        # chromium: pinned by the dev shell, so the recording is reproducible
        # rather than whatever browser the host happens to prefer.
        exe = os.environ.get("PW_CHROMIUM") or shutil.which("chromium")
        if not exe:
            print("no chromium found (set PW_CHROMIUM or use nix develop)", file=sys.stderr)
            return 4

        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=exe, headless=True)
            page = browser.new_page(viewport={"width": width, "height": height})
            page.goto(f"http://127.0.0.1:{args.port}/", wait_until="domcontentloaded")
            open_browsable(page)

            print(f"recording {width}x{height} -> {out}")
            page.screencast.start(path=str(out), size={"width": width, "height": height})

            # The cursor decoration must outlive the whole tour, so it is held
            # open as a context manager rather than disposed per step.
            with page.screencast.show_actions(
                cursor="pointer", duration=900, position="top-right"
            ):
                page.screencast.show_chapter(
                    "Diode Sentinel",
                    description="Intrusion detection on a strictly one-directional feed",
                    duration=2600,
                )
                page.wait_for_timeout(400)

                # 1. Overview, as it lands.
                glide(page, "#kpis")
                page.wait_for_timeout(700)
                glide(page, "#timeline-chart")
                page.wait_for_timeout(700)

                # 2. Alert queue: click in, then let a severity chip filter the
                #    queue live. The chip is a toggle, so it is clicked a second
                #    time to clear -- otherwise the tour could reach step 4 with
                #    an empty table and nothing to open.
                glide(page, 'a.nav-link[href="#alerts"]')
                page.click('a.nav-link[href="#alerts"]')
                page.wait_for_timeout(900)
                chip = '#filters .chip[data-sev="critical"]'
                if glide(page, chip):
                    page.click(chip)
                    page.wait_for_timeout(1300)
                    page.click(chip)  # toggle off, back to the full queue
                    page.wait_for_timeout(900)

                # 3. Free-text search -- typed, not pasted, so the cursor sits
                #    over the field and keystrokes are visible.
                if glide(page, "#search"):
                    page.click("#search")
                    page.locator("#search").press_sequentially("exfil", delay=95)
                    page.wait_for_timeout(1300)
                    page.locator("#search").fill("")
                    page.wait_for_timeout(900)

                # 4. Open one record and show the evidence the detector emitted.
                page.screencast.show_chapter(
                    "Inspect one record",
                    description="Evidence as emitted by the detector, with its limits stated",
                    duration=1800,
                )
                if glide(page, "#alert-rows tr[data-key]"):
                    page.click("#alert-rows tr[data-key]")
                    page.wait_for_timeout(1500)
                    # The raw evidence sits inside a collapsed <details>, so it
                    # has no box until the summary is clicked. Expand it, then
                    # travel down to it.
                    if glide(page, "#detail-modal details.raw-evidence > summary", steps=12):
                        page.click("#detail-modal details.raw-evidence > summary")
                        page.wait_for_timeout(700)
                    glide(page, "#detail-evidence", steps=14, settle_ms=200)
                    page.wait_for_timeout(1400)
                    glide(page, '#detail-modal button[aria-label="Close"]')
                    page.click('#detail-modal button[aria-label="Close"]')
                    page.wait_for_timeout(900)

                # 5. The project's actual contribution: what a directional feed
                #    cannot see at all.
                page.screencast.show_chapter(
                    "What cannot be observed",
                    description="Five PS-26145 features are structurally unobservable one-way",
                    duration=2200,
                )
                page.wait_for_timeout(500)
                glide(page, "#sensor-strip")
                page.wait_for_timeout(1500)

            page.screencast.stop()
            browser.close()
    finally:
        srv.terminate()
        try:
            srv.wait(timeout=5)
        except subprocess.TimeoutExpired:
            srv.kill()

    if not out.exists() or out.stat().st_size == 0:
        print("recording produced no output", file=sys.stderr)
        return 5
    print(f"wrote {out} ({out.stat().st_size / 1024:.0f} KiB)")

    if not args.no_mp4:
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            print("ffmpeg not on PATH; leaving the WebM as-is", file=sys.stderr)
            return 0
        mp4 = out.with_suffix(".mp4")
        # H.264 + yuv420p + faststart: plays in every browser and in the deck.
        subprocess.run(
            [
                ffmpeg, "-y", "-v", "error", "-i", str(out),
                "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                str(mp4),
            ],
            check=True,
        )
        print(f"wrote {mp4} ({mp4.stat().st_size / 1024:.0f} KiB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
