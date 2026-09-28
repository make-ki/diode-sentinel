"""
Packet readers: uniform packet-tuple streams from pcap files.

Two backends:
  - iter_dpkt:   dpkt (fast, pure-python parsing, much faster dissection)
  - iter_scapy:  scapy PcapReader (slow; reference implementation for parity)

Both yield identical tuples so run.py's pipeline is backend-agnostic:
    (t, src, dst, proto, sport, dport, size, is_syn, payload, qname, seq,
     qtype)
where t is sim-relative seconds, payload is raw TCP/UDP bytes (b"" if none),
qname is the DNS question name for UDP/53 queries (else None), size is the
full frame length (consistent across backends), and seq is the TCP sequence
number (0 for UDP).
"""
import socket

from config import SIM_START

try:
    import dpkt
    HAVE_DPKT = True
except ImportError:
    HAVE_DPKT = False


def _dns_qname(payload: bytes):
    """Extract the question name from a raw DNS query payload.

    Returns (qname, qtype) or (None, None). The question's record type sits
    immediately after the terminating zero label, so it costs nothing to
    capture here -- and it is one-way observable by construction, since the
    client writes it into the query before it ever leaves the network.
    """
    if len(payload) < 17:
        return None, None
    off = 12                                   # skip DNS header
    labels = []
    try:
        while off < len(payload):
            n = payload[off]
            if n == 0:
                break
            if n & 0xC0:                       # compression pointer (responses)
                return None, None
            off += 1
            if off + n > len(payload):
                return None, None
            labels.append(payload[off:off + n].decode(errors="replace"))
            off += n
        # off now sits on the root label's zero byte; the 2-byte qtype and
        # 2-byte qclass follow it.
        if off + 5 > len(payload):
            return None, None
        qtype = int.from_bytes(payload[off + 1:off + 3], "big")
    except IndexError:
        return None, None
    qname = ".".join(labels) + "." if labels else None
    return qname, qtype


def iter_dpkt(path: str):
    import dpkt
    with open(path, "rb") as fh:
        for ts, buf in dpkt.pcap.Reader(fh):
            t = float(ts) - SIM_START
            eth = dpkt.ethernet.Ethernet(buf)
            ip = eth.data
            if not isinstance(ip, dpkt.ip.IP):
                continue
            src = socket.inet_ntoa(ip.src)
            dst = socket.inet_ntoa(ip.dst)
            if isinstance(ip.data, dpkt.tcp.TCP):
                tcp = ip.data
                is_syn = bool(tcp.flags & dpkt.tcp.TH_SYN) \
                    and not (tcp.flags & dpkt.tcp.TH_ACK)
                yield (t, src, dst, "tcp", tcp.sport, tcp.dport, len(buf),
                       is_syn, bytes(tcp.data), None, tcp.seq, None)
            elif isinstance(ip.data, dpkt.udp.UDP):
                udp = ip.data
                qname = qtype = None
                if udp.dport == 53:
                    qname, qtype = _dns_qname(bytes(udp.data))
                yield (t, src, dst, "udp", udp.sport, udp.dport, len(buf),
                       False, bytes(udp.data), qname, 0, qtype)


def iter_scapy(path: str):
    from scapy.utils import PcapReader
    from scapy.layers.inet import IP, TCP, UDP
    from scapy.layers.dns import DNS
    with PcapReader(path) as pr:
        for pkt in pr:
            if IP not in pkt:
                continue
            t = float(pkt.time) - SIM_START
            ip = pkt[IP]
            if TCP in pkt:
                tcp = pkt[TCP]
                flags = int(tcp.flags)
                yield (t, ip.src, ip.dst, "tcp", int(tcp.sport),
                       int(tcp.dport), len(pkt),
                       bool(flags & 0x02 and not flags & 0x10),
                       bytes(tcp.payload), None, int(tcp.seq), None)
            elif UDP in pkt:
                udp = pkt[UDP]
                qname = qtype = None
                if int(udp.dport) == 53 and pkt.haslayer(DNS):
                    try:
                        q = pkt[DNS].qd
                        if isinstance(q, list):
                            q = q[0]
                        qname = q.qname.decode(errors="replace")
                        qtype = int(q.qtype)
                    except Exception:
                        pass
                yield (t, ip.src, ip.dst, "udp", int(udp.sport),
                       int(udp.dport), len(pkt), False, bytes(udp.payload),
                       qname, 0, qtype)


def best_reader():
    """(name, iterator_fn) -- dpkt preferred, scapy fallback."""
    return ("dpkt", iter_dpkt) if HAVE_DPKT else ("scapy", iter_scapy)
