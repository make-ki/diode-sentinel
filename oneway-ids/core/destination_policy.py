"""Offline operator authorisation, never inferred from cloud ownership.

Matching uses source/destination IP, transport, port and observed byte volume;
all traffic inputs are one-way observable. The registry is operator context,
not a measured network feature. No network queries are performed.
"""
import ipaddress
import json


class DestinationPolicy:
    def __init__(self, entries=()):
        self.entries = []
        for row in entries:
            required = {"name", "source", "destination", "protocol", "port",
                        "volume_class", "max_bytes"}
            if set(row) != required:
                raise ValueError("destination entry requires exactly: " + ", ".join(sorted(required)))
            if row["protocol"] not in ("tcp", "udp"):
                raise ValueError("protocol must be tcp or udp")
            if type(row["port"]) is not int or not 1 <= row["port"] <= 65535:
                raise ValueError("port must be an integer in 1..65535")
            if type(row["max_bytes"]) is not int or row["max_bytes"] <= 0:
                raise ValueError("max_bytes must be a positive integer")
            if any(not isinstance(row[k], str) or not row[k].strip()
                   for k in ("name", "volume_class")):
                raise ValueError("name and volume_class must be nonempty strings")
            self.entries.append((dict(row), ipaddress.ip_network(row["source"]),
                                 ipaddress.ip_network(row["destination"])))

    @classmethod
    def load(cls, path):
        with open(path) as fh:
            rows = json.load(fh)
        if not isinstance(rows, list):
            raise ValueError("destination registry must be a JSON list")
        return cls(rows)

    def match(self, src, dst, endpoints, total):
        """Require every observed (protocol, port) to be explicitly authorised.

        The byte cap applies to the whole young transfer, not each port. An
        unknown endpoint fails closed. Cloud ownership alone never authorises.
        """
        if not endpoints:
            return None
        source, destination = ipaddress.ip_address(src), ipaddress.ip_address(dst)
        matches = []
        for protocol, port in sorted(endpoints):
            candidates = [row for row, snet, dnet in self.entries
                          if source in snet and destination in dnet
                          and row["protocol"] == protocol and row["port"] == port
                          and total <= row["max_bytes"]]
            if not candidates:
                return None
            matches.append(candidates[0])
        return {"registry_entries": sorted({r["name"] for r in matches}),
                "volume_classes": sorted({r["volume_class"] for r in matches})}
