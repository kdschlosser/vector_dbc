# MIT License
#
# Copyright (c) 2021 Kevin Schlosser
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


class SignalGroup(object):
    """
    A CAN signal group. Signal groups are used to define a group of
    signals within a message, e.g. to define that the signals of a
    group have to be updated in common.
    """

    def __init__(self, parent, name, repetitions=1, signal_names=None):
        self._name = name
        self._repetitions = repetitions
        self._signal_names = signal_names if signal_names else []
        self._parent = parent

    @property
    def message(self):
        return self._parent

    @property
    def name(self):
        """The signal group name as a string."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def repetitions(self):
        """The signal group repetitions."""
        return self._repetitions

    @repetitions.setter
    def repetitions(self, value):
        self._repetitions = value

    @property
    def signals(self):
        """The signals in this group"""
        return [signal for signal in self._parent.signals if signal.name in self._signal_names]

    @signals.setter
    def signals(self, value):
        sig_names = []

        for signal in value:
            if signal.message != self._parent:
                raise ValueError('signal must be mapped to the message of this signal group')

            if signal.name not in sig_names:
                sig_names += [signal.name]

        self._signal_names = sig_names[:]

    def __str__(self):
        all_sig_names = list(map(lambda sig: sig.name, self._parent.signals))
        self._signal_names = list(filter(
            lambda sig_name: sig_name in all_sig_names, self._signal_names
        ))

        return 'SIG_GROUP_ {frame_id} {signal_group_name} {repetitions} : {signal_names};'.format(
            frame_id=self._parent.dbc_frame_id,
            signal_group_name=self.name,
            repetitions=self.repetitions,
            signal_names=' '.join(self._signal_names)
        )

