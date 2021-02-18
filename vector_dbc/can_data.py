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
    def frame_id(self):
        return int(self._frame_id)

    @frame_id.setter
    def frame_id(self, frame_id):
        self._frame_id = frame_id

    def set_sending_node(self, node):
        tp_tx_indentfier = node.tp_tx_indentfier

        if tp_tx_indentfier is not None:
            if isinstance(self._frame_id, J1939FrameId):
                self._frame_id.source_address = tp_tx_indentfier

            elif isinstance(self._frame_id, GMParameterIdExtended):
                self._frame_id.source_id = tp_tx_indentfier


class RXData(dict):
    _frame_id = None

    @property
    def frame_id(self):
        return int(self._frame_id)

    @frame_id.setter
    def frame_id(self, frame_id):
        self._frame_id = frame_id

