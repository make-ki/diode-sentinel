# Shannon Entropy in This IDS

## What it is

Shannon entropy measures how unpredictable or spread out a set of values is.
It is expressed in bits and is calculated as:

$$
H(X) = -\sum_i p_i \log_2(p_i)
$$

Here, $p_i$ is the proportion of observations belonging to value $i$.

For a packet window containing source IP addresses:

- If every packet has the same source, the distribution is concentrated and
  entropy is `0` bits.
- If packets are evenly distributed across many source IPs, entropy is higher.
- With $N$ equally common values, the maximum is $\log_2(N)$ bits.

Entropy is therefore about the *distribution*, not just the number of unique
values. Two windows can have the same number of source IPs but different
entropy if one is dominated by a single source.

## The implementation

The shared helper is `shannon_entropy` in `detectors.py`:

```python
def shannon_entropy(counter) -> float:
    n = sum(counter.values())
    if n == 0:
        return 0.0
    return -sum((c / n) * math.log2(c / n)
                for c in counter.values())
```

It accepts a `Counter`-like object whose values are occurrence counts. It first
turns each count into a probability, applies the formula above, and returns a
floating-point number in bits. An empty counter returns `0.0` instead of
attempting `log2(0)`.

## How this repository uses it

### DGA detection: a decision feature

`DGADetector.on_dns` takes the first label of a DNS name, such as `x7k29m...`,
and counts its characters with `Counter(label)`. The resulting character
entropy is combined with:

- label length;
- vowel ratio; and
- digit ratio.

The lexical gate requires a label at least `DGA_MIN_LEN` characters long and
an entropy of at least `DGA_MIN_ENTROPY` (`3.3` bits in `config.py`), plus the
configured vowel/digit condition. A source must produce the configured streak
of high-entropy labels before a Tier-1 DGA alert is emitted.

Entropy helps identify labels that look machine-generated: random-looking
strings tend to use many characters with relatively even frequencies, while
ordinary words reuse a smaller set of characters. It is only one signal. The
optional character CNN can confirm labels that the scalar lexical gate misses.

### DDoS detection: evidence, not the branch condition

`DDosDetector.on_window` calculates entropy over the source-IP counts in each
traffic window and includes it in spoofed-flood alert evidence as
`src_ip_entropy_bits`.

The spoofed-source branch actually triggers on packet volume and
`distinct_src_ips >= DDOS_MIN_SPOOF_SRCS` (`500` by default). This is
intentional: distinct-source cardinality gives a stable operational threshold,
while entropy provides useful context about how evenly those sources
contributed traffic. The SYN-flood branch uses the SYN ratio and can include a
dominant-source attribution when the source distribution is concentrated.

## Small example

Suppose four observations have counts `{a: 4}`. The only probability is
$p(a)=1$, so the entropy is `0` bits.

For `{a: 2, b: 2}`, the probabilities are `0.5` and `0.5`:

$$
H = -(0.5\log_2 0.5 + 0.5\log_2 0.5) = 1 \text{ bit}
$$

For `{a: 3, b: 1}`, the entropy is about `0.81` bits. It has the same two
distinct values as `{a: 2, b: 2}`, but less uncertainty because `a` dominates.

## Important limitations

Entropy does not understand meaning. A benign random identifier can have high
entropy, and a malicious dictionary-based DGA can have low entropy. Short
strings also make empirical entropy estimates noisy and biased low because
there are too few samples for character frequencies to settle. That is why the
DNS detector combines entropy with length and lexical ratios, requires a
streak, and optionally uses a sequence model.

Entropy also does not reveal packet direction or response behavior. This IDS is
one-way by design, so the calculation uses only observations available on the
outbound feed.

## Where to read next

- [Detector implementation](../detectors.py)
- [Detection thresholds](../config.py)
- [DGA and CNN discussion](../README.md#dga-tier-item-10-a-character-cnn-and-why-it-earns-its-place)
- [Simulation guide](run-simulation.md)