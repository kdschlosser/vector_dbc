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

class GMParameterIdExtended(object):

    def __init__(self, priority, parameter_id, source_id):
        self._priority = priority
        self._parameter_id = parameter_id
        self._source_id = source_id

    @property
    def priority(self):
        return self._priority

    @property
    def parameter_id(self):
        return self._parameter_id

    @property
    def source_id(self):
        return self._source_id

    @source_id.setter
    def source_id(self, source_id):

        self._source_id = source_id

    @property
    def frame_id(self):
        frame_id = self.priority & 0x7
        frame_id <<= 13
        frame_id |= self.parameter_id & 0x1FFF
        frame_id <<= 13
        frame_id |= self.source_id & 0x1FFF

        return frame_id

    @classmethod
    def from_frame_id(cls, frame_id):
        priority = (frame_id >> 26) & 0x7
        parameter_id = (frame_id >> 13) & 0x1FFF
        source_id = frame_id & 0x1FFF

        return cls(priority, parameter_id, source_id)

    def __eq__(self, other):
        if isinstance(other, int):
            other = self.from_frame_id(other)
            return other == self

        elif isinstance(other, GMParameterIdExtended):
            return other.parameter_id == self.parameter_id

        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __int__(self):
        return self.frame_id

    def __str__(self):
        return str(int(self))

    def __repr__(self):
        template = 'GMParameterIdExtended(priority=0x{0}, parameter_id=0x{1}, source_id=0x{3})'
        return template.format(
            hex(self.priority)[2:].upper(),
            hex(self.parameter_id)[2:].upper().zfill(4),
            hex(self.source_id)[2:].upper().zfill(4)
        )


class GMParameterId(object):

    def __init__(self, request_type, arbitration_id):
        self._request_type = request_type
        self._arbitration_id = arbitration_id

    @property
    def request_type(self):
        return self._request_type

    @property
    def arbitration_id(self):
        return self._arbitration_id

    @property
    def frame_id(self):
        return self._request_type << 8 | self._arbitration_id

    @classmethod
    def from_frame_id(cls, frame_id):
        request_type = (frame_id >> 8) & 0xFF
        arbitration_id = frame_id & 0xFF
        return cls(request_type, arbitration_id)

    def __eq__(self, other):
        if isinstance(other, int):
            other = self.from_frame_id(other)
            return other == self

        elif isinstance(other, GMParameterId):
            return other.arbitration_id == self.arbitration_id

        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __int__(self):
        return self.frame_id

    def __str__(self):
        return str(int(self))

    def __repr__(self):
        template = 'GMParameterId(request_type=0x{0}, arbitration_id=0x{1})'
        return template.format(
            hex(self.request_type)[2:].upper().zfill(2),
            hex(self.arbitration_id)[2:].upper().zfill(2)
        )
