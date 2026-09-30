#!/usr/bin/env python3
"""Build Diode-Sentinel.pptx from PRESENTATION.md.

Why this exists
---------------
The shipped .pptx drifted from the markdown source and came to describe a
stack that does not exist (Zeek/Suricata, Kafka/Flink, ONNX, K8s). This
script is the single build path from the honest source to slides, so the
deck can be regenerated in one command and can never silently drift again.

Every string below is copied from PRESENTATION.md (the verified source) or
from a measured artifact in the repo. Do not add a technology name here
without confirming it exists in the codebase -- the fictional stack got in
exactly that way.

Usage:  .venv/bin/python build_deck.py   # -> ../Diode-Sentinel.pptx
"""
from __future__ import annotations

import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "Diode-Sentinel.pptx")

# Palette: dark SOC-console look, high contrast for projection.
BG = RGBColor(0x0D, 0x11, 0x17)
PANEL = RGBColor(0x16, 0x1B, 0x22)
INK = RGBColor(0xE6, 0xED, 0xF3)
MUTED = RGBColor(0x9D, 0xA5, 0xB0)
ACCENT = RGBColor(0x58, 0xA6, 0xFF)
GOOD = RGBColor(0x3F, 0xB9, 0x50)
WARN = RGBColor(0xD2, 0x99, 0x22)
BAD = RGBColor(0xF8, 0x54, 0x46)
MONO = RGBColor(0x79, 0xC0, 0xFF)

W, H = Inches(13.333), Inches(7.5)


def _blank(prs: Presentation):
    return prs.slides.add_slide(prs.slide_layouts[6])


def _bg(slide):
    """Solid dark background."""
    r = slide.shapes.add_textbox(0, 0, W, H)
    r.fill.solid()
    r.fill.fore_color.rgb = BG
    r.line.fill.background()
    return r


def title(slide, text, sub=None, color=INK):
    """Slide title + optional subtitle."""
    tb = slide.shapes.add_textbox(Inches(0.55), Inches(0.28), W - Inches(1.1), Inches(0.75))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(30)
    p.font.bold = True
    p.font.color.rgb = color
    if sub:
        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.size = Pt(14)
        p2.font.color.rgb = MUTED
    return tb


def bullets(slide, items, x=0.55, y=1.25, width=None, height=None, size=16,
            gap=6):
    """Body bullets. Each item is (text, level, color)."""
    width = width or (W - Inches(1.1))
    # y may be a plain float (inches); normalise to EMU.
    y_emu = y if isinstance(y, int) else Inches(y)
    height = height or (H - y_emu - Inches(0.35))
    tb = slide.shapes.add_textbox(Inches(x), y_emu, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    first = True
    for text, level, color in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.text = text
        p.level = level
        p.font.size = Pt(size if level == 0 else size - 2)
        p.font.color.rgb = color or INK
        p.space_after = Pt(gap)
    return tb


def _emu(v):
    """Accept a float inch count or an already-EMU int; return EMU."""
    return v if isinstance(v, int) else Inches(v)


def panel(slide, x, y, w, h, fill=PANEL):
    """A rounded panel to hold a table or callout."""
    from pptx.enum.shapes import MSO_SHAPE
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, _emu(x), _emu(y),
                               _emu(w), _emu(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    s.line.color.rgb = RGBColor(0x30, 0x38, 0x44)
    s.shadow.inherit = False
    return s


def visual_card(slide, x, y, w, h, eyebrow, heading, body, accent=ACCENT):
    """Compact diagram card using editable PowerPoint shapes and text."""
    from pptx.enum.shapes import MSO_SHAPE
    panel(slide, x, y, w, h)
    stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, _emu(x), _emu(y),
                                   Inches(0.055), _emu(h))
    stripe.fill.solid(); stripe.fill.fore_color.rgb = accent
    stripe.line.fill.background()
    tb = slide.shapes.add_textbox(_emu(x + 0.2), _emu(y + 0.1),
                                  _emu(w - 0.35), _emu(h - 0.16))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0
    tf.margin_top = 0; tf.margin_bottom = 0
    p = tf.paragraphs[0]; p.text = eyebrow.upper()
    p.font.size = Pt(9); p.font.bold = True; p.font.color.rgb = accent
    p.space_after = Pt(4)
    p = tf.add_paragraph(); p.text = heading
    p.font.size = Pt(17); p.font.bold = True; p.font.color.rgb = INK
    p.space_after = Pt(3)
    p = tf.add_paragraph(); p.text = body
    p.font.size = Pt(11); p.font.color.rgb = MUTED
    return tb


def diagram_arrow(slide, x, y, text="→", size=25):
    tb = slide.shapes.add_textbox(_emu(x), _emu(y), Inches(0.48), Inches(0.42))
    p = tb.text_frame.paragraphs[0]; p.text = text
    p.font.size = Pt(size); p.font.bold = True; p.font.color.rgb = ACCENT
    p.alignment = PP_ALIGN.CENTER
    return tb


def table(slide, rows, x, y, w, col_w=None, size=12, header=True, hsize=12):
    """rows[0] is the header. Column widths in inches when given."""
    nrows, ncols = len(rows), len(rows[0])
    h = Inches(0.34 * nrows)
    gf = slide.shapes.add_table(nrows, ncols, _emu(x), _emu(y), _emu(w), h)
    t = gf.table
    if col_w:
        total = sum(col_w)
        for i, cw in enumerate(col_w):
            t.columns[i].width = Emu(int(Inches(w) * cw / total))
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = t.cell(r, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(0x1C, 0x22, 0x2B) if r == 0 else PANEL
            cell.margin_left = Inches(0.08)
            cell.margin_right = Inches(0.06)
            cell.margin_top = Inches(0.02)
            cell.margin_bottom = Inches(0.02)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.text = str(val)
            p.font.size = Pt(hsize if r == 0 else size)
            p.font.bold = (r == 0 and header)
            p.font.color.rgb = ACCENT if r == 0 else INK
    return t


def callout(slide, text, y=6.15, color=WARN, label=None):
    """The 'say this line' quote box at the foot of a slide."""
    panel(slide, 0.55, y, W - Inches(1.1), 0.95, RGBColor(0x1A, 0x16, 0x0E))
    tb = slide.shapes.add_textbox(Inches(0.75), Inches(y + 0.10),
                                  W - Inches(1.5), Inches(0.75))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (label + "  " if label else "") + text
    p.font.size = Pt(15)
    p.font.italic = True
    p.font.color.rgb = color


def build():
    prs = Presentation()
    prs.slide_width = W
    prs.slide_height = H

    # ---------------------------------------------------------------- 1 title
    s = _blank(prs); _bg(s)
    tb = s.shapes.add_textbox(Inches(0.8), Inches(2.0), W - Inches(1.6), Inches(3.4))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Diode Sentinel"
    p.font.size = Pt(58); p.font.bold = True; p.font.color.rgb = ACCENT
    for line, sz, col in [
        ("AI-Based Detection of Cyber Threats in Unidirectional IP Traffic", 22, INK),
        ("PS-26145 · NTRO · Software · Blockchain & Cybersecurity", 16, MUTED),
        ("", 8, MUTED),
        ("Every claim below is anchored to a file you can open on stage.", 15, GOOD),
        ("Where something is a gap, the deck says so.", 15, GOOD),
    ]:
        q = tf.add_paragraph(); q.text = line
        q.font.size = Pt(sz); q.font.color.rgb = col
        q.space_after = Pt(8)

    # ------------------------------------------------- 2 the one-line framing
    s = _blank(prs); _bg(s)
    title(s, "A threat detector inside a room with no door",
          "The framing that reframes every judge question")
    panel(s, 0.55, 1.5, W - Inches(1.1), 1.7, RGBColor(0x14, 0x1A, 0x24))
    tb = s.shapes.add_textbox(Inches(0.85), Inches(1.75), W - Inches(1.7), Inches(1.2))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = ("“The statement does not ask for a threat detector. It asks for a "
              "threat detector inside a room with no door. Anyone can run an IDS "
              "on a mirror port; the entire difficulty is that we are forbidden "
              "from asking the network a single question.”")
    p.font.size = Pt(21); p.font.italic = True; p.font.color.rgb = INK
    visual_card(s, 0.85, 3.72, 3.25, 1.35, "Protected network",
                "Transmit side", "One-way traffic leaves the protected zone.", GOOD)
    diagram_arrow(s, 4.32, 4.13)
    visual_card(s, 5.02, 3.72, 3.25, 1.35, "Hardware boundary",
                "Data diode", "Copies packets across; provides no return path.", WARN)
    diagram_arrow(s, 8.5, 4.13)
    visual_card(s, 9.2, 3.72, 3.25, 1.35, "Monitoring enclave",
                "Receive side", "Parse, score, and review observed evidence.", ACCENT)
    panel(s, 1.45, 5.45, 10.45, 0.67, RGBColor(0x14, 0x1A, 0x24))
    note = s.shapes.add_textbox(Inches(1.7), Inches(5.58), Inches(10), Inches(0.36))
    p = note.text_frame.paragraphs[0]
    p.text = "No probes   ·   No response-side telemetry   ·   No payload decryption"
    p.font.size = Pt(16); p.font.color.rgb = MUTED; p.alignment = PP_ALIGN.CENTER

    # --------------------------------------------- 3 the observability contract
    s = _blank(prs); _bg(s)
    title(s, "The observability contract — our actual contribution",
          "core/observability.py · 21 rows · each cites the feature, the PS class, the status, the reason")
    # The rendered image of the whole contract; generated by
    # build_contract_image.py from the same CONTRACT list the CI gate enforces,
    # so the picture can never drift from the code it depicts.
    img_path = os.path.join(HERE, "contract.png")
    if os.path.exists(img_path):
        s.shapes.add_picture(img_path, Inches(0.45), Inches(1.18),
                             width=Inches(7.7))
    else:
        table(s, [
            ["Status", "Count", "Meaning"],
            ["OBSERVABLE", "15", "computed from the feed; row cites the consuming function"],
            ["IMPOSSIBLE", "5", "information-theoretically absent; row states the physical reason"],
            ["SUBSTITUTED", "1", "requested signal is impossible; a one-way proxy replaces it"],
        ], x=0.55, y=1.55, w=7.6, col_w=[1.6, 0.8, 4.6], size=14, hsize=14)
    bullets(s, [
        ("Every team will build detectors. The finding no other submission will "
         "have is knowing which requested features can exist at all.", 0, INK),
        ("The contract is enforced, not descriptive.", 0, ACCENT),
        ("tests/test_contract.py scans detector sources for forbidden "
         "bidirectional tokens — ja3s, server_hello, rcode, nxdomain, ttl, "
         "rtt, bytes_in, in_out_ratio — and FAILS THE BUILD on a hit.", 1, INK),
        ("Verified to fail on an injected rcode read and pass once removed.", 1, MUTED),
        ("UDP reflection needs response size, which the diode hides. We expose "
         "source fan-out and many-source shared-target burst proxies, with the "
         "threshold and measurements in each alert; neither claims amplification.", 0, INK),
        ("The five IMPOSSIBLE rows are named with the physical reason each is "
         "absent — and the substitute we use instead.", 0, INK),
    ], x=8.45, y=1.35, width=4.3, size=14)

    # ------------------------------------ 4 the five impossible PS features
    s = _blank(prs); _bg(s)
    title(s, "Five requested features are impossible under the PS’s own constraint",
          "This is a finding about the problem statement, not a limitation of our code")
    table(s, [
        ["PS class", "Requested feature", "Why it cannot exist one-way"],
        ["(d)", "JA3S / JA4S server fingerprint", "computed from the ServerHello — sent by the responder, the wrong direction"],
        ["(d)", "negotiated cipher / server certificate", "both chosen by the responder after the handshake, off the observable path"],
        ["(b)", "round-trip time", "needs the response; one-way latency is unmeasurable without a return path"],
        ["(c)", "NXDOMAIN ratio", "RCODE lives in the DNS response header, which the diode never delivers"],
        ["(f)", "outbound-to-inbound byte ratio", "the inbound half is never seen, so the ratio has no denominator"],
    ], x=0.55, y=1.55, w=12.2, col_w=[0.9, 3.4, 7.9], size=13, hsize=13)
    callout(s, "“Five of the features the problem statement asks us to implement are made "
               "impossible by the problem statement’s own first constraint. That is not our "
               "limitation — it is the geometry of a diode. A detector that reads one anyway "
               "does not fail loudly, it silently produces garbage, so we made the contract "
               "enforceable rather than descriptive.”", y=5.35, color=GOOD)

    # ------------------------------------------------------- 5 what we did instead
    s = _blank(prs); _bg(s)
    title(s, "Where a feature is impossible, we built the closest observable substitute",
          "and put the substitute’s arithmetic on the alert so it can be audited")
    bullets(s, [
        ("Exfiltration — the ratio has no denominator one-way. Instead:", 0, ACCENT),
        ("cumulative bytes to a (src, dst) pair the source has never spoken to, and", 1, INK),
        ("that total against the source’s own median bytes per window, with a "
         "pair-age guard so a long transfer cannot slip under the bar in later windows.", 1, INK),
        ("Every exfil alert carries bytes_to_new_dst, src_baseline_bytes_median, "
         "ratio_vs_baseline, pair_age_windows.  (core/detectors.py → ExfilDetector)", 1, MUTED),
        ("DGA — the standard pipeline counts NXDOMAINs, which is a response. Instead:", 0, ACCENT),
        ("detect from the query alone: character entropy + lexical profile + a streak "
         "requirement. The alert states the limitation in its own evidence.", 1, INK),
        ("TLS — JA3S and server-side fields are off the table. Instead:", 0, ACCENT),
        ("JA4 (client) with JA3 alongside; every alert states that server-side fields "
         "are invisible. A wrong fingerprint is worse than no fingerprint, so we wrote "
         "an ACK-less sequence tracker for retransmits and gaps.", 1, INK),
    ], y=1.35, size=15)

    # ------------------------------------------------------------------ 6 QUIC
    s = _blank(prs); _bg(s)
    title(s, "The one place the cryptography hands you the metadata for free",
          "QUIC Initial packets are decryptable with no secret at all")
    bullets(s, [
        ("RFC 9001 derives the QUIC Initial keys from a public version salt plus the "
         "connection ID — no secret, no key material, no certificate.", 0, INK),
        ("So we recover ClientHello metadata from QUIC on a one-way feed, where TLS server "
         "fingerprints are structurally impossible.", 0, INK),
        ("We proved it rather than asserted it:", 0, ACCENT),
        ("RFC 9001 Appendix A.1/A.2 key and packet vectors validate the parse "
         "(tests/test_quic.py); QUIC uses JA4 prefix q, TLS uses t.", 1, INK),
        ("Tampered packets and unsupported versions are rejected.", 1, INK),
        ("This is not “decryption” of payload: the Initial is decryptable by "
         "protocol design, with public inputs. No payload content is ever read.", 0, MUTED),
    ], y=1.35, size=16)
    callout(s, "Judge follow-up to prep: “isn’t that decryption?” → No payload is "
               "decrypted. It is the one place the protocol design exposes the metadata "
               "for free.", y=5.9, color=GOOD)

    # ------------------------------------------- 7 streaming + replay evidence
    s = _blank(prs); _bg(s)
    title(s, "Streaming, timing and replay reproducibility",
          "Two constraints that eliminate most submissions")
    flow = [
        ("INGEST", "One-way packets", "Capture or pcap stream", ACCENT),
        ("PARSE", "Decode frames", "Count malformed / sampled", GOOD),
        ("ASSEMBLE", "Flows + windows", "2 s idle · 10 s window", WARN),
        ("DETECT", "Rules + models", "Observable fields only", ACCENT),
        ("PRESENT", "Alert + dashboard", "Record appears as emitted", GOOD),
    ]
    x_positions = [0.55, 3.05, 5.55, 8.05, 10.55]
    for i, (tag, heading, body, color) in enumerate(flow):
        visual_card(s, x_positions[i], 1.52, 2.22, 1.43, tag, heading, body, color)
        if i < len(flow) - 1:
            diagram_arrow(s, x_positions[i] + 2.24, 2.0, size=20)
    visual_card(s, 0.8, 3.45, 5.65, 2.35, "Timing + sensor",
                "The clock closes the window",
                "The ≤2 s flow-idle timeout and ≤10 s window set the processing bounds; "
                "they are not a measured p95 latency claim. One-second health heartbeats "
                "continue while the source is idle. Packet-stream kernel drops stay unknown.", WARN)
    visual_card(s, 6.85, 3.45, 5.65, 2.35, "Replay + backend parity",
                "Current archive: 45 / 67",
                "14,049-packet capture; preserved refs remain 46 / 68. One invalid synthetic-QUIC "
                "tls_known_malware record was removed; fixture migration is pending. Current "
                "dpkt and Scapy alert records match. This is replay evidence, not chain of custody.", GOOD)
    panel(s, 1.7, 6.18, 9.9, 0.53, RGBColor(0x14, 0x1A, 0x24))
    note = s.shapes.add_textbox(Inches(1.9), Inches(6.27), Inches(9.5), Inches(0.3))
    p = note.text_frame.paragraphs[0]
    p.text = "Paced FIFO smoke: alerts observed while replay writer and analysis pipeline are still active"
    p.font.size = Pt(12); p.font.color.rgb = MUTED; p.alignment = PP_ALIGN.CENTER

    # --------------------------------------------- 8 the operator experience
    s = _blank(prs); _bg(s)
    title(s, "DEMO 01 · Open the live overview",
          "Active replay · the alert queue and sensor status update as traffic arrives")
    dashboard_image = os.path.join(HERE, "presentation_assets",
                                   "dashboard-live-demo.png")
    if os.path.exists(dashboard_image):
        s.shapes.add_picture(dashboard_image, Inches(0.55), Inches(1.42),
                             width=Inches(7.35))
    else:
        panel(s, 0.55, 1.42, 7.35, 5.35)
        bullets(s, [("See dashboard-live-demo.png for the captured application view.",
                     0, INK)], x=0.85, y=2.0, width=6.7, size=15)
    visual_card(s, 8.2, 1.55, 4.55, 1.42, "Stream",
                "Alerts arrive during replay",
                "Dashboard starts first; the pipeline writes each alert as it fires.", GOOD)
    visual_card(s, 8.2, 3.25, 4.55, 1.42, "Evidence",
                "Counts describe records",
                "Rule, model and correlation records stay distinct; correlations reuse signals.", ACCENT)
    visual_card(s, 8.2, 4.95, 4.55, 1.42, "Sensor health",
                "Measured status stays visible",
                "Heartbeat, last packet and counts; pcap kernel drops remain unknown.", WARN)
    cap = s.shapes.add_textbox(Inches(0.55), Inches(6.98), Inches(7.4), Inches(0.26))
    p = cap.text_frame.paragraphs[0]
    p.text = "Synthetic traffic and simulated local indicator · no external threat feed claimed"
    p.font.size = Pt(9); p.font.color.rgb = MUTED

    # ------------------------------------------ 9 inspect and scope an alert
    s = _blank(prs); _bg(s)
    title(s, "DEMO 02 · Inspect a signal, then pivot to its source",
          "The screenshots capture two real interactions in the running dashboard")
    review_image = os.path.join(HERE, "presentation_assets", "alert-review-demo.png")
    if os.path.exists(review_image):
        s.shapes.add_picture(review_image, Inches(0.55), Inches(1.42),
                             width=Inches(8.1))
    else:
        panel(s, 0.55, 1.42, 8.1, 5.55)
    visual_card(s, 8.9, 1.48, 3.85, 1.48, "Step 1 · Open alert",
                "Periodic flow pattern",
                "Six observed flows · mean interval 4.98 s · CV 0.0179 against a 0.15 gate.", ACCENT)
    visual_card(s, 8.9, 3.22, 3.85, 1.48, "Step 2 · Read limits",
                "Pattern is evidence, not proof",
                "Scheduled jobs and cloud telemetry can look periodic. Scores are not calibrated probabilities.", WARN)
    visual_card(s, 8.9, 4.96, 3.85, 1.48, "Step 3 · Scope source",
                "Filter to the observed host",
                "Compare its flow times with the host schedule; return to the full queue to restore context.", GOOD)
    cap = s.shapes.add_textbox(Inches(0.55), Inches(7.12), Inches(8.0), Inches(0.24))
    p = cap.text_frame.paragraphs[0]
    p.text = "Synthetic replay · one-way client metadata · no successful session inferred"
    p.font.size = Pt(9); p.font.color.rgb = MUTED

    # ----------------------------------------- 10 source pivot in the queue
    s = _blank(prs); _bg(s)
    title(s, "DEMO 03 · Filter the queue to the selected source",
          "An analyst can narrow the evidence and clear the filter to restore full scope")
    pivot_image = os.path.join(HERE, "presentation_assets", "source-pivot-demo.png")
    if os.path.exists(pivot_image):
        s.shapes.add_picture(pivot_image, Inches(0.55), Inches(1.42),
                             width=Inches(8.1))
    else:
        panel(s, 0.55, 1.42, 8.1, 5.55)
    visual_card(s, 8.9, 1.55, 3.85, 1.5, "Selected entity",
                "Source 10.0.0.7",
                "The queue narrows to records matching this observed source. The count reflects the captured moment.", ACCENT)
    visual_card(s, 8.9, 3.4, 3.85, 1.5, "Review in context",
                "Compare signals over time",
                "Check the host’s other observed destinations and alert sequence; clear the filter to return to all records.", GOOD)
    visual_card(s, 8.9, 5.25, 3.85, 1.5, "Interpret carefully",
                "A pivot is not a verdict",
                "Source association helps triage; it does not establish compromise or intent.", WARN)

    # ------------------------------------------------------------- 11 DDoS class a
    s = _blank(prs); _bg(s)
    title(s, "Class (a) — three answers to have ready before a judge notices",
          "Volumetric / protocol DDoS from flow-level rate and source-IP entropy")
    visual_card(s, 0.7, 1.55, 5.85, 1.72, "TCP / mixed traffic",
                "Spoofed-source volume",
                "≥500 distinct sources selects `ddos_volumetric_spoofed`; SYN ratio stays "
                "in the evidence. On the reference capture it is about 0.93.", ACCENT)
    visual_card(s, 6.8, 1.55, 5.85, 1.72, "UDP · one source",
                "Fan-out across endpoints",
                "≥100 datagrams and ≥20 destination IP/port endpoints in one 10 s window.", GOOD)
    visual_card(s, 0.7, 3.62, 5.85, 1.72, "UDP · many sources",
                "Shared-target burst",
                "≥1,000 datagrams from ≥50 visible source IPs to one endpoint in the window.", WARN)
    visual_card(s, 6.8, 3.62, 5.85, 1.72, "Why not call it amplification?",
                "Replies never cross the diode",
                "Packet rates, endpoints and trigger thresholds are observed. Response size "
                "is missing; these prototype thresholds need capture calibration.", MUTED)
    panel(s, 1.15, 5.85, 11.0, 0.7, RGBColor(0x14, 0x1A, 0x24))
    note = s.shapes.add_textbox(Inches(1.4), Inches(5.98), Inches(10.5), Inches(0.42))
    p = note.text_frame.paragraphs[0]
    p.text = "Source cardinality drives the spoofed-source decision; Shannon entropy is recorded as supporting evidence."
    p.font.size = Pt(14); p.font.color.rgb = MUTED; p.alignment = PP_ALIGN.CENTER

    # ------------------------------------------------------------- 12 throughput
    s = _blank(prs); _bg(s)
    title(s, "Throughput — stated and demonstrated, as the statement requires",
          "Pure Python, one CPU core, no C extension, no GPU")
    table(s, [
        ["Mode", "Packets/s", "Sustained rate", "Flows/s"],
        ["Rules only (dpkt)", "≈ 48,600 – 50,400", "≈ 240 Mbps", "≈ 19,200 – 20,300"],
        ["With ML tier (LightGBM)", "≈ 24,000 – 31,000", "≈ 120 – 155 Mbps", "≈ 9,700 – 11,800"],
    ], x=0.55, y=1.5, w=12.2, col_w=[3.2, 2.6, 2.4, 2.6], size=14, hsize=14)
    bullets(s, [
        ("This capture: 14,049 packets, 8,622,217 bytes, 598.8 s, mean packet 613.7 B, "
         "5,225 distinct flows (4,617 SYN-only, 720 DNS, 7,107 TLS).", 0, INK),
        ("The ML tier is quoted as a range on purpose: it varies with model warm-up and "
         "cache state, so a single false-precision number would not be reproducible.", 0, MUTED),
        ("For a SYN flood the binding number is packets/s, not Mbps — small packets are "
         "cheaper per byte. pkt/s is the honest headline; Mbps is the translation the "
         "statement asks for, using this capture’s mean packet size.", 0, INK),
    ], y=3.2, size=15)
    callout(s, "“About 50,000 packets per second — roughly 240 Mbps sustained — on a single "
               "CPU core, in pure Python with no C extension and no GPU. With the ML tier "
               "scoring every closed flow it drops to roughly 24 to 31 thousand.”",
            y=6.0, color=GOOD)
    tb = s.shapes.add_textbox(Inches(0.55), Inches(7.0), W - Inches(1.1), Inches(0.4))
    p = tb.text_frame.paragraphs[0]
    p.text = ("Do not lead with the real-time factor: the capture is sparse (≈ 23 pkt/s ≈ 0.11 Mbps), "
              "so “~2,000× real-time” is one measurement restated. Quote it only as a repeatability claim.")
    p.font.size = Pt(11); p.font.color.rgb = WARN

    # ------------------------------------------------------------- 13 coverage
    s = _blank(prs); _bg(s)
    title(s, "Coverage and false positives — the measured answer, not the headline you want")
    bullets(s, [
        ("6/6 PS threat classes covered. The rules tier emits 12 distinct threat classes "
         "(13 with the ML tier): historical recorded capture 46/68; current archived capture 45/67, plus 20 "
         "benign periodic events suppressed by the allowlist.", 0, INK),
        ("On the historical default capture all 46 rules-tier alerts land on hosts the generator "
         "designates as attackers — zero FPs.", 0, GOOD),
        ("But we built a deliberate FP-pressure variant (MESSY=1) that injects benign "
         "patterns a real network has: first-time cloud backups, low-jitter IoT telemetry, "
         "CDN-style long subdomain labels.", 0, WARN),
        ("On it the rules tier emits ONE TRUE CRITICAL FP — data_exfiltration at 0.95 on "
         "the benign backup host — because “large sustained upload to a never-before-seen "
         "destination” is exactly what a backup is.", 1, INK),
        ("Explicit demo operator approval keeps that alert visible at medium / 0.60. "
         "Registry is empty by default: this is triage, not improved detection accuracy.", 1, WARN),
        ("The allowlist count is not a result either: ALLOWLIST is operator-curated against "
         "the same telemetry IPs the generator emits, so “zero FPs after allowlisting” is "
         "partly circular.", 0, MUTED),
        ("The shipped ML tier under the same pressure: 79 ml_flow_suspicious alerts, "
         "59 on designated benign hosts. This is the measured reason the "
         "rules tier stays primary and the ML tier is quorum-gated.", 0, WARN),
        ("Maturity signal worth quoting: per-flow ML on bare SYN packets produced 3,021 "
         "alerts; excluding bare SYNs at the tier boundary brought it to 20, all on true "
         "attack hosts.", 0, INK),
    ], y=1.3, size=14)

    # --------------------------------------------------------------- 14 the models
    s = _blank(prs); _bg(s)
    title(s, "The models — measured, including the negative results",
          "Synthetic evaluation; new replay experiment holds out t ≥ 420 s")
    bullets(s, [
        ("Replay experiment: shipped vs new model flags 35/541 vs 2/541 benign flows; "
         "both detect 60/75 malicious flows at 0.95. New fit holds out t ≥ 420 s; "
         "old model exposure is unverified. Synthetic only; shipped model unchanged.", 0, INK),
        ("Category 5–7 (models567/eval.json) — four of six work:", 0, ACCENT),
        ("encrypted_xgb, sequence_cnn, scan_rf and exfil_xgb all reach recall 1.000 at "
         "0 benign FP on the temporal holdout (t ≥ 390 s).", 1, GOOD),
        ("The other two are the IsolationForest pair, and they are a MEASURED NEGATIVE "
         "RESULT, not a tuning issue: they detect every malicious row, but only at "
         "thresholds that also fire on 2–6% of benign windows.", 1, WARN),
        ("Classifier recall remains 0.000. Serving now attaches raw anomaly scores only "
         "to supervised alerts corroborated by a same-window rule; no standalone IF alerts.", 1, INK),
        ("The more interesting half: scan_rf and exfil_xgb used to read 0.000 too, and "
         "that was not a model failure — the split placed every malicious scan and exfil "
         "row in training, so the holdout had nothing to score. Once attack bursts landed "
         "on both sides of the split, the same architectures scored perfectly. "
         "“Unmeasurable” and “broken” are different claims.", 0, INK),
    ], y=1.3, size=14.5)

    # ------------------------------------------------------------- 15 DGA CNN
    s = _blank(prs); _bg(s)
    title(s, "The DGA character CNN — the strongest model result in the repo",
          "numpy only, 4,930 parameters, no torch, no GPU")
    table(s, [
        ["Held-out family", "CNN recall", "Rule recall"],
        ["hex_like (same kind, unseen family)", "1.000", "0.473"],
        ["dictionary_pair (different kind)", "0.007", "0.004"],
        ["benign FP rate", "0.001", "0.003"],
    ], x=0.55, y=1.5, w=6.4, col_w=[3.4, 1.2, 1.2], size=13, hsize=13)
    bullets(s, [
        ("Family-held-out: one family of each kind is held out entirely.", 0, MUTED),
        ("On the demo capture the CNN caught a real DGA query the rules called benign — "
         "8yuxczaumapqpp, entropy 3.182 against a 3.3 gate.", 0, INK),
        ("The dictionary row is presented too: morphology alone cannot settle dictionary "
         "DGA, which is why the CNN is a quorum-gated confirmer, never critical.", 0, INK),
        ("Its analytic gradients match finite differences to 7e-09 — a real conv1d, "
         "with hand-written backprop, not a framework call.", 0, MUTED),
    ], x=7.3, y=1.5, width=5.4, size=13.5)
    callout(s, "“On our demo capture the CNN caught a real DGA query the rules called "
               "benign — entropy 3.182 against a 3.3 gate. That miss is caused by the exact "
               "short-string entropy bias we documented before we built the model.”",
            y=4.6, color=GOOD)

    # ------------------------------------------------- 16 external corpus + quorum
    s = _blank(prs); _bg(s)
    title(s, "Scored as shipped on a real external corpus",
          "andrewaeva/DGA · 694,173 real DGA domains (8 families) vs 1,000,000 Alexa domains")
    bullets(s, [
        ("The rules have a blind spot we predicted:", 0, ACCENT),
        ("the entropy gate’s 10-character floor scores 0.019 / 0.000 TPR on conficker and "
         "pushdo (median labels 8 chars); the CNN, which has no floor, scores 0.886 / 0.446 "
         "on exactly those families.", 1, INK),
        ("The CNN alone is not deployable:", 0, WARN),
        ("its per-string FP rate on 1M real benign domains is 16.5% — real hostnames "
         "include ccmhw, 7ri-rj, 059455, which no morphology model separates from DGA. "
         "That is the measured reason the quorum exists.", 1, INK),
        ("The shipped quorum is a measured constant, not a guess:", 0, ACCENT),
        ("swept against 1M benign queries: 17.3 alerts/hour on a purely benign host at k=2, "
         "0.46 at k=4 with 7 of 8 families still detected.", 1, INK),
        ("The honest cost, said out loud: at k=4 the demo capture no longer shows a "
         "CNN-only alert — the sensor that cried wolf 17×/hour was worse than missing "
         "one label.", 1, WARN),
        ("Also owned: rovnix and matsnu are not separated per-string (0.226 / 0.257) and no "
         "CNN threshold fixes it; mixed-host precision at 5% DGA prevalence is 0.171. The "
         "layered policy is what keeps the benign case quiet, not the CNN alone.", 0, MUTED),
    ], y=1.3, size=14)

    # --------------------------------------------------------- 17 IoT-23 validation
    s = _blank(prs); _bg(s)
    title(s, "Validated against real malware — IoT-23",
          "CTU Stratosphere Laboratory, 2020, CC-BY-4.0 · shipped detector, nothing retuned")
    table(s, [
        ["Scenario", "Malware", "Alerts", "Host recall", "Host precision"],
        ["Capture-8-1", "Hakai", "206", "1.000", "1.000"],
        ["Capture-1-1", "HideNSeek", "38,401", "1.000 (infected host, 0 clean FPs)", "—"],
        ["Capture-42-1", "Trojan", "0", "0.000 — a total miss", "—"],
        ["Honeypot-4-1", "benign HUE", "8", "—", "0.000 — real FP"],
    ], x=0.55, y=1.5, w=12.2, col_w=[2.0, 1.5, 1.3, 4.0, 3.0], size=12.5, hsize=12.5)
    bullets(s, [
        ("Scoring is per host, not per flow: Mirai worm-spread makes one infected host emit "
         "tens of thousands of “benign” scan flows, so per-flow precision looks like 0.017 "
         "when the detector is right. A host is the unit an analyst responds to.", 0, INK),
        ("The C2-beaconing detector generalises to real malware with no retuning — perfect "
         "host recall on two different families on two different captures. Periodicity is "
         "periodicity regardless of the botnet.", 0, GOOD),
        ("A real, honest miss: Capture-42-1 has six malicious C&C flows and we raised zero. "
         "Say this before anyone finds it.", 0, WARN),
        ("A real, structural FP: the benign Philips HUE smart bulb phoning home to Google "
         "and AWS fires as C2 beaconing — low-jitter periodic traffic to a small set of "
         "cloud destinations is exactly what beaconing looks like one-way. Not a tuning bug; "
         "a fundamental confound for a one-way egress monitor.", 0, WARN),
    ], y=3.9, size=13.5)

    # ------------------------------------------------------------------- 18 gaps
    s = _blank(prs); _bg(s)
    title(s, "Gaps — own them before a judge finds them",
          "Volunteering a limitation reads as rigour; getting caught reads as an overclaim")
    bullets(s, [
        ("UDP has source fan-out and shared-target burst proxies with packet rates, "
         "counts and prototype trigger thresholds. They need capture calibration. "
         "Response size is unavailable, so reflection/amplification is not inferred. "
         "Slowloris is a dataset suggestion, not a scored class; its one-way long-lived "
         "flow proxy remains future work.", 0, INK),
        ("The circularity of our own generator is real and partly answered: temporal splits, "
         "published label noise, an external corpus scored as shipped, and the IoT-23 run "
         "above — two families, one honest miss, one structural FP.", 0, INK),
        ("The stage demo starts the dashboard before paced synthetic FIFO replay; alerts "
         "arrive during replay, and sensor status shows heartbeat, last packet, counts and "
         "unknown kernel drops honestly. A physical AF_PACKET interface run remains "
         "unverified because this container has CapBnd: 0.", 0, WARN),
        ("240 Mbps is extrapolated from a 0.11 Mbps capture: fair, dissection is O(1) per "
         "packet so pkt/s generalises, and the 1-in-N sampling guard exists precisely "
         "because the pure-Python ceiling is ~50k pkt/s — above it we degrade coverage "
         "deterministically and report the loss rather than hide it.", 0, INK),
        ("The IoT-23 category 5–7 models did not fire on any real scenario — still "
         "unvalidated on real traffic.", 0, MUTED),
    ], y=1.3, size=14)

    # -------------------------------------- 19 things that exist because one-way
    s = _blank(prs); _bg(s)
    title(s, "Things in the repo that exist only because of the constraint",
          "Each is a direct consequence of one-way, not a generic feature")
    bullets(s, [
        ("Cross-signal fusion (not asked for): two weak one-way signals become one strong "
         "verdict — beacon + known-bad JA4 → confirmed_c2_implant; beacon + DGA → "
         "botnet_c2_with_dga. Fire-on-escalation so an incident does not re-fire every window.", 0, INK),
        ("Restart-safe fingerprint inventory (--state): without warm-start, a sensor "
         "restart blinds novelty detection for another baseline period — exactly the "
         "window an attacker would choose. The baseline gate is skipped on warm load.", 0, INK),
        ("Baseline poisoning prevention: known-bad TLS handshakes are never fed into the "
         "inventory, so an ongoing attack cannot teach the sensor that it is normal.", 0, INK),
        ("Operator-curated allowlist, deliberately not auto-learned: auto-learning periodic "
         "traffic whitelists existing botnets.", 0, INK),
        ("Evidence-scaled statistical gates: sampling CV at n=6 is noisy (a benign process "
         "dips under a fixed gate ~2% of the time), so the gate is tight for small n and "
         "standard for n ≥ 10. Found by a real benign DNS poll landing at CV 0.2249 against "
         "a 0.25 gate.", 0, INK),
        ("Every alert carries a human-readable why next to the machine-readable features — "
         "a label plus a score is not triageable at 03:00.", 0, INK),
        ("A second, independently trained model on a different input type: the DGA CNN reads "
         "the string, the flow model reads tabular statistics. Different data, different "
         "failure modes, and the CNN’s win is attributable to a documented bias in the "
         "rules rather than to “more ML”.", 0, INK),
    ], y=1.3, size=13.5)

    # ------------------------------------------------- 20 closing / three things
    s = _blank(prs); _bg(s)
    title(s, "If you only remember three sentences", color=ACCENT)
    bullets(s, [
        ("“Five of the features the problem statement requests are impossible under its own "
         "first constraint — we enumerated them, substituted one-way signals, and made the "
         "constraint enforceable in CI so the code cannot silently reach for a response "
         "that never arrives.”", 0, INK),
        ("“The clock closes our windows, not the traffic — that is the difference between "
         "bounded latency and an end-of-run report.”", 0, INK),
        ("“We ran it against real malware on IoT-23, not just our own generator: two "
         "families detected with no retuning, one honest miss, and one false positive that "
         "is structural to one-way monitoring rather than a bug.”", 0, INK),
    ], y=1.6, size=19, gap=16)
    panel(s, 0.55, 5.7, W - Inches(1.1), 1.0, RGBColor(0x14, 0x1A, 0x24))
    tb = s.shapes.add_textbox(Inches(0.8), Inches(5.85), W - Inches(1.6), Inches(0.8))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = ("Current archive 45 / 67; historical refs 46 / 68 (migration pending) · 6/6 classes · "
              "~50k pkt/s single-core pure Python · no GPU and no response-side fields.")
    p.font.size = Pt(15); p.font.color.rgb = MUTED; p.alignment = PP_ALIGN.CENTER

    prs.save(OUT)
    return len(prs.slides.__iter__.__self__._sldIdLst)


if __name__ == "__main__":
    n = build()
    print(f"wrote {OUT} ({n} slides)")
