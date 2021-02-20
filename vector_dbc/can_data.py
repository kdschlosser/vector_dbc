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

from .frame_id import (
    J1939FrameId,
    GMParameterIdExtended,
)


class TXData(bytearray):
    _frame_id = None

    @property
    def hex(self):
        return ' '.join(hex(item)[2:].upper().zfill(2) for item in self)

    @property
    def frame_id_hex(self):
        return self._frame_id.hex

    @property
    def frame_id(self):
        return int(self._frame_id)

    @frame_id.setter
    def frame_id(self, value):
        self._frame_id = value

    def set_sending_node(self, node):
        tp_tx_indentfier = node.tp_tx_indentfier

        if tp_tx_indentfier is not None:
            if isinstance(self._frame_id, J1939FrameId):
                self._frame_id.source_address = tp_tx_indentfier

            elif isinstance(self._frame_id, GMParameterIdExtended):
                self._frame_id.source_id = tp_tx_indentfier


class RXData(list):
    _frame_id = None

    @property
    def frame_id(self):
        return int(self._frame_id)

    @frame_id.setter
    def frame_id(self, value):
        self._frame_id = value

    def __getitem__(self, item):
        if isinstance(item, int):
            return list.__getitem__(self, item)

        for signal in self:
            if signal.name == item:
                return signal

        raise KeyError('"{0}" cannot be found.'.format(item))

    def __setitem__(self, key, value):
        if isinstance(key, int):
            list.__setitem__(self, key, value)
            return

        for i, signal in enumerate(self):
            if signal.name == key:
                self[i] = value
                return

        self.append(value)

    def __contains__(self, item):
        if isinstance(item, bytes):
            item = item.decode('utf-8')

        if isinstance(item, str):
            for signal in self:
                if signal.name == item:
                    return True

            return False

        return list.__contains__(self, item)
