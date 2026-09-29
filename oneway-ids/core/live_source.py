#!/usr/bin/env python3
"""
Live packet source: AF_PACKET raw socket (stdlib only).

Yields exactly the same packet tuples as pcap_reader, and dissects with the
same dpkt calls, so live and offline share ONE dissection path -- the same
way dpkt and scapy already share the 9-tuple contract for parity testing.

Three things a file reader never needs and a live socket
always does:

  drain()          a bounded receive loop. The driver pulls a batch, then
                   regains control to advance the stream clock, so a link
                   that goes silent still closes flows and windows on time.
  stats()          kernel drop accounting (PACKET_STATISTICS). Loss on a
                   one-way feed is silent by definition -- if we do not
                   report it, nobody can.
  line-rate guard  LINE_RATE_SAMPLE. Pure-Python dissection tops out near
                   45k pkt/s on one core; on a fatter link a deterministic
                   1-in-N sample keeps windows statistically representative
                   instead of letting the kernel ringbuffer drop arbitrary
                   packets (which biases rate estimates unpredictably).

Privileges: AF_PACKET needs CAP_NET_RAW, and promiscuous mode needs
CAP_NET_ADMIN. Opening the socket therefore fails for an unprivileged user;
open() translates that into CapturePermissionError with the fix, rather than
a bare traceback.

Kernel BPF note: attaching a filter requires assembling a struct sock_filter
program, which this module does not do. Filtering here is Python-side
(port_filter) applied AFTER dissection -- it saves detector work, not parse
work. Use scapy's AsyncSniffer if you need real kernel-side BPF.
"""
import errno
import os
import select
import socket
import struct
import time

from core.config import (CAPTURE_BATCH, CAPTURE_RCVBUF, CAPTURE_TIMEOUT,
                    LINE_RATE_SAMPLE)
from core.pcap_reader import _dns_qname

try:
    import dpkt
    HAVE_DPKT = True
except ImportError:                       # pragma: no cover
    HAVE_DPKT = False

ETH_P_ALL = 3
SOL_PACKET = 263
PACKET_ADD_MEMBERSHIP = 1
PACKET_MR_PROMISC = 1
PACKET_STATISTICS = 6
SO_TIMESTAMP = getattr(socket, "SO_TIMESTAMP", 29)


def _align(epoch: float) -> float:
    """Floor a capture anchor to the whole second.

    Tumbling windows are aligned to stream time zero, so the anchor decides
    where EVERY window boundary falls. Flooring to the second keeps those
    boundaries on wall-clock seconds instead of wherever a sensor happened to
    start -- otherwise two sensors started a second apart score different
    windows over the same incident, which is exactly what makes cross-sensor
    correlation and time-based reporting awkward.

    It also makes a replayed capture reproduce the offline analysis exactly
    rather than shifting every window by a sub-second offset.
    """
    return float(int(epoch))


class CapturePermissionError(RuntimeError):
    """Raised when the capture socket cannot be opened for lack of privilege."""


class CaptureConfigError(RuntimeError):
    """Raised when the capture REQUEST is wrong -- an interface that does not
    exist, or an impossible batch/sample setting. Kept distinct from
    CapturePermissionError because the fix is completely different: one needs
    a different interface name, the other needs different privileges."""


def list_interfaces() -> list:
    """Interface names the kernel currently has.

    Reads /sys/class/net rather than ioctl'ing, so there is no netifaces
    dependency and no platform plumbing.
    """
    try:
        return sorted(os.listdir("/sys/class/net"))
    except OSError:
        return []


def _device_exists(name: str) -> bool:
    if os.path.isdir("/sys/class/net"):
        return os.path.exists(os.path.join("/sys/class/net", name))
    try:                       # non-Linux fallback
        socket.if_nametoindex(name)
        return True
    except OSError:
        return False


def _parse_packet_stats(raw: bytes):
    """PACKET_STATISTICS -> (packets, drops).

    Kernel returns struct tpacket_stats { unsigned int tp_packets;
    unsigned int tp_drops; } -- 8 bytes, and READING IT RESETS IT, so the
    values are deltas since the previous call, not lifetime totals.
    """
    if len(raw) < 8:
        return (0, 0)
    return struct.unpack("II", raw[:8])


def _cmsg_timestamp(ancdata):
    """Extract SCM_TIMESTAMP (struct timeval) from recvmsg ancillary data.

    Kernel receive timestamps are the accurate ones under load: by the time
    userspace gets around to reading, several batches may have queued, and
    time.time() would stamp all of them with the drain time. That skew
    directly corrupts beacon IAT statistics, which are the whole signal for
    threat class (b). Returns None if no timestamp cmsg is present.
    """
    for level, ctype, cdata in ancdata:
        if level != socket.SOL_SOCKET or ctype != SO_TIMESTAMP:
            continue
        if len(cdata) >= 16:                       # 64-bit timeval
            sec, usec = struct.unpack("ll", cdata[:16])
            return sec + usec / 1e6
        if len(cdata) >= 8:                        # 32-bit timeval
            sec, usec = struct.unpack("ii", cdata[:8])
            return sec + usec / 1e6
    return None


class AfPacketSource:
    """Captures from a network interface via AF_PACKET SOCK_RAW.

    anchor: the epoch that stream-relative time is measured from. Defaults to
    the wall clock at construction, so t starts near 0 and the detector's
    BASELINE_SECONDS window means "the first 3 minutes of this capture" --
    which is what a live sensor actually wants.
    """

    def __init__(self, iface, anchor=None, batch=CAPTURE_BATCH,
                 rcvbuf=CAPTURE_RCVBUF, timeout=CAPTURE_TIMEOUT,
                 sample=LINE_RATE_SAMPLE, promisc=True, snaplen=65535,
                 port_filter=None):
        if not HAVE_DPKT:
            raise RuntimeError("live capture needs dpkt for dissection")
        self.iface = iface
        self.anchor = _align(anchor if anchor is not None else time.time())
        self.batch = batch
        self.rcvbuf = rcvbuf
        self.timeout = timeout
        self.sample = max(int(sample), 1)
        self.promisc = promisc
        self.snaplen = snaplen
        self.port_filter = set(port_filter) if port_filter else None

        self.sock = None
        self.seen = 0              # frames received from the kernel
        self.sampled_out = 0       # frames deliberately skipped by the sampler
        self.non_ipv4 = 0          # ARP/LLDP/IPv6/etc -- counted, not parsed
        self.other_ip = 0          # IPv4 but neither TCP nor UDP (ICMP, GRE,
                                   # ESP...) -- parsed, then dropped, because
                                   # every detector is TCP/UDP-shaped
        self.malformed = 0         # undissectable frames
        self._counter = 0
        self._dropped = 0

    # -- lifecycle ---------------------------------------------------------
    def open(self):
        if self.sock is not None:
            return self
        # Validate the device BEFORE touching the socket: a typo should say so
        # in one line, not surface as ENODEV from deep inside if_nametoindex.
        if not _device_exists(self.iface):
            raise CaptureConfigError(_NO_DEVICE.format(
                iface=self.iface,
                available=", ".join(list_interfaces()) or "(none found)"))
        try:
            sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW,
                                 socket.htons(ETH_P_ALL))
        except PermissionError as e:
            raise CapturePermissionError(_PERM_HELP.format(iface=self.iface)) \
                from e
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.rcvbuf)
            if self.promisc:
                mreq = struct.pack("ihh8s",
                                   socket.if_nametoindex(self.iface),
                                   PACKET_MR_PROMISC, 0, b"")
                sock.setsockopt(SOL_PACKET, PACKET_ADD_MEMBERSHIP, mreq)
            sock.bind((self.iface, 0))
            sock.settimeout(self.timeout)
            try:
                sock.setsockopt(socket.SOL_SOCKET, SO_TIMESTAMP, 1)
            except OSError:
                pass               # no kernel timestamps: fall back to time.time()
        except PermissionError as e:
            sock.close()
            raise CapturePermissionError(_PERM_HELP.format(iface=self.iface)) \
                from e
        except OSError as e:
            sock.close()
            if e.errno in (errno.ENODEV, errno.ENXIO, errno.EINVAL):
                raise CaptureConfigError(_NO_DEVICE.format(
                    iface=self.iface,
                    available=", ".join(list_interfaces()) or "(none found)")) \
                    from e
            raise
        self.sock = sock
        return self

    def close(self):
        if self.sock is not None:
            try:
                self.sock.close()
            finally:
                self.sock = None

    def __enter__(self):
        return self.open()

    def __exit__(self, *exc):
        self.close()
        return False

    # -- accounting --------------------------------------------------------
    def stats(self):
        """(frames_seen, kernel_drops) as deltas since the last call.

        Named deltas because PACKET_STATISTICS is read-and-clear. Cumulative
        counters live on the object (seen / sampled_out / non_ip / malformed).
        """
        if self.sock is None:
            return (0, 0)
        try:
            raw = self.sock.getsockopt(SOL_PACKET, PACKET_STATISTICS, 8)
        except OSError:
            return (0, 0)
        return _parse_packet_stats(raw)

    def snapshot(self) -> dict:
        """Cumulative counters, for reports and periodic logging.

        Every received frame lands in exactly one bucket, so 'analysed' can
        never claim frames that were quietly discarded -- a frame that does
        not become a packet must show up as non-IPv4, non-TCP/UDP, malformed,
        or sampled out.
        """
        return {"iface": self.iface, "seen": self.seen,
                "analysed": (self.seen - self.sampled_out - self.non_ipv4
                             - self.other_ip - self.malformed),
                "sampled_out": self.sampled_out, "non_ipv4": self.non_ipv4,
                "other_ip": self.other_ip,
                "malformed": self.malformed, "sample": self.sample,
                "kernel_dropped": self._dropped}

    # -- capture -----------------------------------------------------------
    def _keep(self) -> bool:
        """Deterministic 1-in-N sampler. Deterministic (not random) so a
        given capture always yields the same packet subset, which keeps
        results reproducible and re-testable."""
        if self.sample <= 1:
            return True
        self._counter += 1
        keep = (self._counter % self.sample) == 0
        if not keep:
            self.sampled_out += 1
        return keep

    def dissect(self, buf, ts):
        """Raw frame -> packet tuple, identical in shape and meaning to
        pcap_reader.iter_dpkt. Non-IP frames return None."""
        try:
            eth = dpkt.ethernet.Ethernet(buf)
        except Exception:
            self.malformed += 1
            return None
        ip = eth.data
        if not isinstance(ip, dpkt.ip.IP):
            self.non_ipv4 += 1             # ARP, LLDP, IPv6, ...
            return None
        t = ts - self.anchor
        try:
            src = socket.inet_ntoa(ip.src)
            dst = socket.inet_ntoa(ip.dst)
        except Exception:
            self.malformed += 1
            return None
        if isinstance(ip.data, dpkt.tcp.TCP):
            tcp = ip.data
            is_syn = bool(tcp.flags & dpkt.tcp.TH_SYN) \
                and not (tcp.flags & dpkt.tcp.TH_ACK)
            return (t, src, dst, "tcp", tcp.sport, tcp.dport, len(buf),
                    is_syn, bytes(tcp.data), None, tcp.seq, None)
        if isinstance(ip.data, dpkt.udp.UDP):
            udp = ip.data
            qname = qtype = None
            if udp.dport == 53:
                qname, qtype = _dns_qname(bytes(udp.data))
            return (t, src, dst, "udp", udp.sport, udp.dport, len(buf),
                    False, bytes(udp.data), qname, 0, qtype)
        # IPv4 but not TCP/UDP: ICMP, GRE, ESP, OSPF... No detector consumes
        # these, so the frame is dropped -- but it is COUNTED, so the report
        # can never imply that unprocessed traffic was analysed.
        self.other_ip += 1
        return None

    def _passes_filter(self, pkt) -> bool:
        if self.port_filter is None:
            return True
        return pkt[5] in self.port_filter or pkt[4] in self.port_filter

    def default_clock(self):
        """Stream-seconds from the wall clock. A socket feed is always live,
        so packet time and wall clock agree by construction, and a silent
        link still advances the clock (which is what closes idle windows)."""
        return lambda: time.time() - self.anchor

    def drain(self, max_batch=None, timeout=None) -> list:
        """Receive up to max_batch frames, waiting at most `timeout` for the
        first one. Returns [] when idle or on timeout, so the caller keeps
        control and can advance its clock."""
        if self.sock is None:
            self.open()
        limit = max_batch or self.batch
        wait = self.timeout if timeout is None else timeout
        out = []
        self.sock.settimeout(wait)
        for _ in range(limit):
            try:
                data, ancdata, _flags, _addr = self.sock.recvmsg(self.snaplen)
            except (socket.timeout, TimeoutError):
                break
            except BlockingIOError:
                break
            except OSError:
                break
            self.seen += 1
            if not self._keep():
                continue
            ts = _cmsg_timestamp(ancdata)
            if ts is None:
                ts = time.time()
            pkt = self.dissect(data, ts)
            if pkt is not None and self._passes_filter(pkt):
                out.append(pkt)
        pkts, drops = self.stats()
        self._dropped += drops
        return out

    def __iter__(self):
        """Convenience iteration; the live driver uses drain() instead so it
        can tick on empty drains."""
        self.open()
        try:
            while True:
                for pkt in self.drain():
                    yield pkt
        finally:
            self.close()


# classic pcap magic -> (struct endian prefix, timestamp divisor)
_PCAP_MAGICS = {
    b"\xd4\xc3\xb2\xa1": ("<", 1e6),      # little-endian, microseconds
    b"\xa1\xb2\xc3\xd4": (">", 1e6),      # big-endian, microseconds
    b"\x4d\x3c\xb2\xa1": ("<", 1e9),      # little-endian, nanoseconds
    b"\xa1\xb2\x3c\x4d": (">", 1e9),      # big-endian, nanoseconds
}
_PCAPNG_MAGIC = b"\x0a\x0d\x0d\x0a"
PCAP_GLOBAL_HDR_LEN = 24
PCAP_RECORD_HDR_LEN = 16
MAX_CAPTURE_LEN = 262144               # libpcap's ceiling for incl_len


_NO_STREAM = """\
no capture stream at {path}

Expected a FIFO (or growing pcap file) that a capture tool is writing, e.g.
  mkfifo {path}
  dumpcap -i <iface> -P -U -w {path}
  run.py --pipe {path}
"""

_PCAPNG_INSTEAD = """\
{path} is carrying pcapng, which cannot be streamed.
Ask the capture tool for classic pcap instead:
  dumpcap -P -U -w {path}
"""

_NOT_PCAP = """\
{path} is not a pcap stream (first 4 bytes: {magic}).
Expected classic pcap from tcpdump/dumpcap, e.g. dumpcap -P -U -w {path}
"""


_NO_DEVICE = """\
no such network interface: {iface}

Available interfaces: {available}
Pick the one carrying the traffic you want to inspect, e.g.
  sudo .venv/bin/python run.py --live <iface>
"""


_PERM_HELP = """\
cannot open a raw capture socket on {iface}: operation not permitted.

AF_PACKET needs CAP_NET_RAW (and CAP_NET_ADMIN for promiscuous mode).
Pick one:
  sudo .venv/bin/python run.py --live {iface}
  sudo setcap cap_net_raw,cap_net_admin+eip $(readlink -f .venv/bin/python)
  docker run --cap-add=NET_RAW --cap-add=NET_ADMIN ...
"""


class PcapStreamSource(AfPacketSource):
    """Capture from a pcap STREAM that another process is writing.

    Splitting capture from analysis: reading a capture stream needs no
    privileges, while opening a capture socket needs CAP_NET_RAW. Keeping
    those separate means the privileged part stays a small, auditable tool
    and the analysis stack never runs as root:

        mkfifo /run/nids/feed.pcap
        dumpcap -i enp7s0 -P -U -w /run/nids/feed.pcap   # file-capped helper
        .venv/bin/python run.py --pipe /run/nids/feed.pcap

    `-P` forces classic pcap (pcapng cannot be streamed) and `-U` makes the
    writer packet-buffered. Leaving out -U makes the writer buffer whole
    seconds of traffic, which silently breaks the latency budget the entire
    design is built on.

    Works equally on a FIFO and on a regular file that is still growing, so
    `--pipe` can also tail a capture in progress. Timestamps come from the
    pcap records themselves, so the stream clock matches the socket path.
    Subclasses AfPacketSource so dissection, sampling and accounting are
    shared verbatim -- one parser, not a second one that drifts.
    """

    def __init__(self, path, anchor=None, batch=CAPTURE_BATCH,
                 timeout=CAPTURE_TIMEOUT, wait=30.0, sample=LINE_RATE_SAMPLE,
                 port_filter=None):
        super().__init__(path, anchor=anchor, batch=batch, timeout=timeout,
                         sample=sample, port_filter=port_filter)
        # AfPacketSource defaults anchor to the wall clock (correct for a live
        # socket). A stream must instead let its FIRST RECORD define t=0, so
        # clear that default unless the caller supplied an anchor -- otherwise
        # t comes out as record_ts minus now, i.e. hugely negative, and every
        # time-based gate in the pipeline (baseline window, tumbling windows,
        # idle timeouts) silently misbehaves.
        self.anchor = float(anchor) if anchor is not None else None
        self.path = path
        self.wait = wait
        self.eof = False
        self._fd = None
        self._buf = bytearray()
        self._pending = []
        self._endian = "<"
        self._ts_div = 1e6
        self._have_global = False
        self._preset_anchor = anchor is not None
        self._last_ts = None           # newest record timestamp seen

    # how far the stream clock may sit from the wall clock before we conclude
    # we are replaying an archive rather than watching a live feed
    LIVE_SKEW_TOLERANCE = 60.0

    def is_live(self) -> bool:
        """True when the stream's timestamps agree with the wall clock.

        A live dumpcap feed timestamps records ~now. A capture replayed from
        an archive does not, and treating the wall clock as authoritative
        there would make every tick jump far past the record timestamps and
        shatter the tumbling windows.
        """
        return (self.anchor is not None
                and abs(time.time() - self.anchor) <= self.LIVE_SKEW_TOLERANCE)

    def default_clock(self):
        """Wall clock for a live feed; None for an archive replay.

        None means "advance the stream clock with packet timestamps", which
        is exactly the offline loop. That distinction matters: a pipe can
        deliver a whole archived capture faster than real time, so a clock
        reading the newest record seen would race ahead of the packets still
        being processed and close every window early. Packet time cannot
        race itself.
        """
        return (lambda: time.time() - self.anchor) if self.is_live() else None

    # -- lifecycle ---------------------------------------------------------
    def open(self):
        if self._fd is not None:
            return self
        if not os.path.exists(self.path):
            raise CaptureConfigError(_NO_STREAM.format(path=self.path))
        try:
            self._fd = os.open(self.path, os.O_RDONLY | os.O_NONBLOCK)
        except OSError as e:
            raise CaptureConfigError(_NO_STREAM.format(path=self.path)) from e
        # Wait for the global header and the first record so t=0 is anchored
        # to real traffic. Skipped when the caller supplied an anchor.
        if not self._preset_anchor:
            deadline = time.monotonic() + self.wait
            while self.anchor is None and not self.eof:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                self._pump(min(remaining, 0.5))
            if self.anchor is None:
                raise CaptureConfigError(_NO_STREAM.format(path=self.path))
        return self

    def close(self):
        if self._fd is not None:
            try:
                os.close(self._fd)
            finally:
                self._fd = None

    # -- parsing -----------------------------------------------------------
    def _pump(self, timeout) -> bool:
        """Wait up to `timeout` for bytes, then parse everything available.
        Returns True if bytes were read."""
        if self._fd is None:
            return False
        try:
            ready, _, _ = select.select([self._fd], [], [], max(timeout, 0.0))
        except InterruptedError:
            return False
        if not ready:
            return False
        got = False
        while True:
            try:
                chunk = os.read(self._fd, 65536)
            except BlockingIOError:
                break
            except InterruptedError:
                continue
            if not chunk:
                self.eof = True          # writer closed the feed
                break
            self._buf += chunk
            got = True
            if len(chunk) < 65536:
                break
        if got:
            self._parse()
        return got

    def _parse(self):
        """Pull complete records out of the buffer; leave a partial tail."""
        if not self._have_global:
            if len(self._buf) < PCAP_GLOBAL_HDR_LEN:
                return
            magic = bytes(self._buf[:4])
            if magic == _PCAPNG_MAGIC:
                raise CaptureConfigError(_PCAPNG_INSTEAD.format(path=self.path))
            entry = _PCAP_MAGICS.get(magic)
            if entry is None:
                raise CaptureConfigError(_NOT_PCAP.format(
                    path=self.path, magic=magic.hex()))
            self._endian, self._ts_div = entry
            del self._buf[:PCAP_GLOBAL_HDR_LEN]
            self._have_global = True

        while len(self._buf) >= PCAP_RECORD_HDR_LEN:
            ts_sec, ts_frac, incl, _orig = struct.unpack_from(
                self._endian + "IIII", self._buf, 0)
            if incl > MAX_CAPTURE_LEN:
                raise CaptureConfigError(_NOT_PCAP.format(
                    path=self.path, magic=bytes(self._buf[:4]).hex()))
            if len(self._buf) < PCAP_RECORD_HDR_LEN + incl:
                return                   # partial record: wait for the rest
            buf = bytes(self._buf[PCAP_RECORD_HDR_LEN:
                                  PCAP_RECORD_HDR_LEN + incl])
            del self._buf[:PCAP_RECORD_HDR_LEN + incl]
            ts = ts_sec + ts_frac / self._ts_div
            if self.anchor is None:
                self.anchor = _align(ts)  # t=0 at the first captured record
            self._last_ts = ts
            self.seen += 1
            if not self._keep():
                continue
            pkt = self.dissect(buf, ts)
            if pkt is not None and self._passes_filter(pkt):
                self._pending.append(pkt)

    # -- capture API (same shape as AfPacketSource) -------------------------
    def drain(self, max_batch=None, timeout=None) -> list:
        """Up to max_batch packets, waiting at most `timeout` for the first.

        [] means idle (the driver still advances its clock); None means the
        feed ended, which stops the driver cleanly instead of spinning.
        """
        if self._fd is None:
            self.open()
        limit = max_batch or self.batch
        wait = self.timeout if timeout is None else timeout
        deadline = time.monotonic() + wait
        while not self._pending and not self.eof:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            if not self._pump(remaining):
                break
        if not self._pending and self.eof:
            return None
        out = self._pending[:limit]
        del self._pending[:limit]
        return out

    def snapshot(self) -> dict:
        snap = super().snapshot()
        snap["source"] = f"pcap stream {self.path}"
        snap["eof"] = self.eof
        return snap
