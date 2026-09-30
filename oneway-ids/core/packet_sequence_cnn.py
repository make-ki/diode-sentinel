"""NumPy 1D CNN adapter for one-way packet-size/timing sequences."""
from core.dga_cnn import CharCnn, MAX_LEN


def _bucket(value, scale):
    value = max(0.0, float(value))
    return min(35, int(value / scale))


def sequence_token(flow, max_packets=MAX_LEN):
    """Encode size, IAT, and outbound direction as a CNN token string."""
    sizes = list(flow.get("packet_sizes", ()))[:max_packets]
    times = list(flow.get("packet_times", ()))[:max_packets]
    tokens = []
    for index, size in enumerate(sizes):
        tokens.append(format(_bucket(size, 64), "x"))
        if index:
            tokens.append(format(_bucket(times[index] - times[index - 1], 0.01), "x"))
        tokens.append("o")
    return "".join(tokens)[:MAX_LEN] or "0"


class PacketSequenceCnn:
    """A trainable 1D CNN over packet-shape tokens.

    The convolution implementation and persistence format are shared with the
    existing NumPy character CNN; only the encoder changes from DNS characters
    to packet size/IAT/direction tokens.
    """

    def __init__(self, model=None):
        self.model = model or CharCnn.new(kernels=(3, 5), filters=32,
                                          dim=16, seed=17, dropout=0.3)

    def score(self, flow):
        return self.model.score(sequence_token(flow))

    def predict_proba(self, flows):
        labels = [sequence_token(flow) for flow in flows]
        return self.model.predict_proba(labels)

    def save(self, path):
        self.model.save(path)

    @classmethod
    def load(cls, path):
        return cls(CharCnn.load(path))
