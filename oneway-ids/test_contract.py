"""CI gate: no detector may read a bidirectional signal.

The observability contract in observability.py is only a claim unless something
fails when it is violated. This test does two things:

  1. verify_contract() -- the contract is internally consistent (every
     OBSERVABLE row cites the function that consumes it, every IMPOSSIBLE row
     states why, every SUBSTITUTED row names its substitute).
  2. scan the detector sources for FORBIDDEN_TOKENS -- the field names a
     bidirectional sensor would read. A hit means someone reached for a signal
     the diode cannot provide, which is the exact failure mode the contract
     exists to prevent.

The token scan is deliberately literal. It does not try to prove a detector is
sound; it fails loudly on the specific, greppable names of response-side
fields. That keeps it honest and keeps it from becoming a test that passes by
construction.
"""

import os
import re
import unittest

import observability

HERE = os.path.dirname(os.path.abspath(__file__))

# Modules that implement detectors or protocol parsing. The contract has no
# business gating test fixtures or the contract file itself.
GATED_MODULES = (
    "detectors.py",
    "tls_meta.py",
    "quic_meta.py",
    "pipeline.py",
    "pcap_reader.py",
    "live_source.py",
    "metrics.py",
)


class TestContractConsistency(unittest.TestCase):
    def test_contract_is_self_consistent(self):
        problems = observability.verify_contract()
        self.assertEqual(problems, [],
                         "contract is inconsistent: " + "; ".join(problems))

    def test_every_ps_class_is_covered(self):
        classes = {r["ps_class"] for r in observability.CONTRACT}
        self.assertEqual(classes, {"a", "b", "c", "d", "e", "f"},
                         "every PS threat class must appear in the contract")

    def test_impossible_features_are_not_claimed_as_detected(self):
        # The alert schema must not advertise a class the contract says is
        # built on an impossible feature. This is the failure that made the
        # old dashboard label DNS tunnelling as though RCODE was used.
        with open(os.path.join(HERE, "detectors.py")) as fh:
            alert_src = fh.read()
        for row in observability.CONTRACT:
            if row["status"] != "IMPOSSIBLE":
                continue
            # the token must not appear as a *consumed* field. Comments are
            # allowed -- documenting an impossibility is the point.
            for token in observability.FORBIDDEN_TOKENS:
                pat = re.compile(r'["\']' + re.escape(token) + r'["\']')
                hits = pat.findall(alert_src)
                self.assertFalse(
                    hits,
                    f"detectors.py reads {token!r}, which contract row "
                    f"{row['feature']!r} declares unobservable one-way")


class TestNoBidirectionalFieldReads(unittest.TestCase):
    """The actual gate. Each forbidden token must be absent from the source
    of every gated module, except inside comments."""

    def _scan(self, path):
        with open(path) as fh:
            for lineno, line in enumerate(fh, 1):
                # strip comments: documenting why a field is NOT used is fine
                code = line.split("#", 1)[0]
                for token in observability.FORBIDDEN_TOKENS:
                    if re.search(r'\b' + re.escape(token) + r'\b', code):
                        yield lineno, token, line.rstrip()

    def test_no_forbidden_field_reads(self):
        failures = []
        for name in GATED_MODULES:
            path = os.path.join(HERE, name)
            if not os.path.exists(path):
                continue
            for lineno, token, line in self._scan(path):
                failures.append(f"{name}:{lineno}: {token} -> {line.strip()}")
        self.assertEqual(
            failures, [],
            "bidirectional field read on a one-way feed:\n  "
            + "\n  ".join(failures))


class TestContractCounts(unittest.TestCase):
    """The numbers quoted on the deck come from here, so they are tested."""

    def test_summary_counts_match_contract(self):
        s = observability.summary()
        total = sum(v for k, v in s["by_class"].items())
        self.assertEqual(s["total"], total)
        self.assertEqual(
            s["observable"] + s["impossible"] + s["substituted"],
            s["total"])

    def test_at_least_one_impossible_feature_named(self):
        # If this ever passes with zero impossible features, the contract has
        # stopped doing its job -- the whole point is that the PS names
        # features its own constraints make unsatisfiable.
        self.assertGreaterEqual(s_impossible(), 3,
                                "contract no longer names any impossible "
                                "feature; it is no longer a contract")


def s_impossible():
    return sum(1 for r in observability.CONTRACT if r["status"] == "IMPOSSIBLE")


if __name__ == "__main__":
    unittest.main()
