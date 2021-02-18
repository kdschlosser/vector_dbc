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
    def signal_names(self):
        """The signal names in the signal group"""
        return self._signal_names

    @signal_names.setter
    def signal_names(self, value):
        self._signal_names = value

    @property
    def signals(self):
        return [signal for signal in self.message.signal if signal.name in self.signal_names]
