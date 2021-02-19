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

from . import gm_parameter_id
from . import j1939

J1939FrameId = j1939.J1939FrameId
GMParameterId = gm_parameter_id.GMParameterId
GMParameterIdExtended = gm_parameter_id.GMParameterIdExtended


class FrameId(object):

    def __init__(self, frame_id):
        self._frame_id = frame_id

    @property
    def hex(self):
        if self.frame_id > 0x7FF:
            return '0x' + hex(self.frame_id)[2:].upper().zfill(8)
        else:
            return '0x' + hex(self.frame_id)[2:].upper().zfill(3)

    def copy(self):
        return FrameId(self._frame_id)

    @classmethod
    def from_frame_id(cls, frame_id):
        return cls(frame_id)

    @property
    def frame_id(self):
        return self._frame_id

    def __eq__(self, other):
        return other == self._frame_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return str(self.frame_id)

    def __int__(self):
        return self._frame_id
