

def _create_mux_ranges(multiplexer_ids):
    """
    Create a list of ranges based on a list of single values.

    Example:
        Input:  [1, 2, 3, 5,      7, 8, 9]
        Output: [[1, 3], [5, 5], [7, 9]]
    """
    ordered = sorted(multiplexer_ids)
    # Anything but ordered[0] - 1
    prev_value = ordered[0]
    ranges = []

    for value in ordered:
        if value == prev_value + 1:
            ranges[-1][1] = value
        else:
            ranges.append([value, value])

        prev_value = value

    return ranges


class SG_MUL_VAL(object):

    def __init__(self, parent, multiplexer_signal, multiplexer_ids):
        self._parent = parent

        signal = [signal for signal in self._parent.message.signals if signal.name == self._multiplexer_signal]
        if len(signal):
            self._multiplexer_signal = signal[0]
        else:
            self._multiplexer_signal = multiplexer_signal

        # for signal in self._parent.message.signals:
        #     if signal.name == self._multiplexer_signal:
        #         self._multiplexer_signal = signal
        #         break
        # else:

        self._multiplexer_ids = multiplexer_ids

    def __radd__(self, other):
        if isinstance(other, tuple):
            other = list(other)
        if not isinstance(other, list):
            other = [other]

        for item in other:
            if item not in self._multiplexer_ids:
                self._multiplexer_ids += [item]

    def __contains__(self, item):
        return item in self._multiplexer_ids

    def __iter__(self):
        return iter(self._multiplexer_ids)

    def __bool__(self):
        return len(self) > 0

    def __len__(self):
        return len(self._multiplexer_ids)

    def __getitem__(self, item):
        return self._multiplexer_ids[item]

    def __setitem__(self, key, value):
        self._multiplexer_ids[key] = value

    @property
    def multiplexer_signal(self):
        if self._multiplexer_signal is None:
            return

        if isinstance(self._multiplexer_signal, _signal.Signal):
            return self._multiplexer_signal

        res = [signal for signal in self._parent.message.signals if signal.name == self._multiplexer_signal]
        if len(res):
            self._multiplexer_signal = res[0]
            return res[0]

    @multiplexer_signal.setter
    def multiplexer_signal(self, value):
        if isinstance(value, _signal.Signal):
            value = value.name

        try:
            signal = self._parent.message.get_signal_by_name(value)
            if not signal.is_multiplexer:
                raise ValueError('signal is not a multiplexer')

        except KeyError:
            raise ValueError('signal not found')

    @property
    def is_ok(self):
        return self._multiplexer_signal is not None

    @property
    def signal(self):
        return self._parent

    def __str__(self):
        if not self.is_ok:
            return ''

        return 'SG_MUL_VAL_ {frame_id} {name} {multiplexer} {ranges};'.format(
            frame_id=self._parent.message.dbc_frame_id,
            name=self._parent.name,
            multiplexer=self.multiplexer_signal.name,
            ranges=', '.join(
                '{}-{}'.format(minimum, maximum)
                for minimum, maximum in _create_mux_ranges(self)
            )
        )


from . import signal as _signal
