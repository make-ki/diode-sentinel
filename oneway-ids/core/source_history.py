"""Bounded source-relative destination history for one-way flow analysis.

The history records whether a (source, destination) pair was seen within
the retained window horizon. It never makes a first-ever claim. If capacity
evicts an entry, later novelty claims for that source are suppressed because
its retained history is no longer complete.
"""
from collections import OrderedDict


class SourceDestinationHistory:
    """Remember recent (source, destination) pairs with explicit coverage.

    ``max_age_windows`` defines the lookback horizon. ``max_entries`` bounds
    memory; capacity eviction marks the affected source's history incomplete.
    A pair absent after age expiry may qualify as new within the retained
    horizon, but evidence must describe the horizon rather than first-ever use.
    """

    def __init__(self, max_age_windows=8640, max_entries=50000):
        if type(max_age_windows) is not int or max_age_windows < 1:
            raise ValueError("max_age_windows must be a positive integer")
        if type(max_entries) is not int or max_entries < 1:
            raise ValueError("max_entries must be a positive integer")
        self.max_age_windows = max_age_windows
        self.max_entries = max_entries
        self._seen = OrderedDict()
        self.incomplete_sources = set()
        self._global_coverage_incomplete = False
        self.expired_entries = 0
        self.evicted_entries = 0

    def _expire(self, idx):
        cutoff = idx - self.max_age_windows
        # Window indices are monotonic in the streaming pipeline, so expired
        # entries form a prefix of insertion/access order.
        while self._seen:
            pair, seen_idx = next(iter(self._seen.items()))
            if seen_idx >= cutoff:
                break
            self._seen.pop(pair)
            self.expired_entries += 1

    def observe(self, src, dst, idx):
        """Return (new_within_horizon, coverage_status) and record this pair."""
        self._expire(idx)
        pair = (src, dst)
        if pair in self._seen:
            self._seen[pair] = idx
            self._seen.move_to_end(pair)
            return False, "complete_within_lookback"

        if self._global_coverage_incomplete or src in self.incomplete_sources:
            return False, "incomplete_after_capacity_eviction"

        self._seen[pair] = idx
        if len(self._seen) > self.max_entries:
            evicted_pair, _ = self._seen.popitem(last=False)
            self.incomplete_sources.add(evicted_pair[0])
            self.evicted_entries += 1
            if len(self.incomplete_sources) > self.max_entries:
                # Keep the loss markers bounded too. Once a marker must be
                # discarded, fail closed for all unknown sources.
                self.incomplete_sources.pop()
                self._global_coverage_incomplete = True
        return True, "complete_within_lookback"

    @property
    def coverage(self):
        return {
            "retained_pairs": len(self._seen),
            "capacity": self.max_entries,
            "max_age_windows": self.max_age_windows,
            "incomplete_sources": len(self.incomplete_sources),
            "global_coverage_incomplete": self._global_coverage_incomplete,
            "expired_entries": self.expired_entries,
            "evicted_entries": self.evicted_entries,
        }

    def coverage_for_source(self, src):
        if self._global_coverage_incomplete or src in self.incomplete_sources:
            return "incomplete_after_capacity_eviction"
        return "complete_within_lookback"
