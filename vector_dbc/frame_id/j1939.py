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

import bitstruct

from ..errors import Error


class J1939FrameId(object):
    def __init__(
        self,
        priority,
        reserved,
        data_page,
        pdu_format,
        pdu_specific,
        source_address
    ):
        self._priority = priority
        self._reserved = reserved
        self._data_page = data_page
        self._pdu_format = pdu_format
        self._pdu_specific = pdu_specific
        self._source_address = source_address

    @classmethod
    def from_pgn(cls, pgn):
        try:
            packed = bitstruct.pack('u18', pgn)
        except bitstruct.Error:
            raise Error(
                'Expected a parameter group number 0..0x3ffff, '
                'but got {}.'.format(hex(pgn)))

        reserved, data_page, pdu_format, pdu_specific = bitstruct.unpack('u1u1u8u8', packed)
        return cls(0, reserved, data_page, pdu_format, pdu_specific, 0)

    @classmethod
    def from_frame_id(cls, frame_id):
        try:
            packed = bitstruct.pack('u29', frame_id)
        except bitstruct.Error:
            raise Error(
                'Expected a frame id 0..0x1fffffff, '
                'but got {}.'.format(hex(frame_id)))

        return cls(*bitstruct.unpack('u3u1u1u8u8u8', packed))

    @property
    def priority(self):
        return self._priority

    @property
    def reserved(self):
        return self._reserved

    @property
    def data_page(self):
        return self._data_page

    @property
    def pdu_format(self):
        return self._pdu_format

    @property
    def pdu_specific(self):
        return self._pdu_specific

    @property
    def source_address(self):
        return self._source_address

    @source_address.setter
    def source_address(self, source_address):
        self._source_address = source_address

    @property
    def frame_id(self):
        try:
            packed = bitstruct.pack(
                'u3u1u1u8u8u8', self.priority, self.reserved, self.data_page,
                self.pdu_format, self.pdu_specific, self.source_address)
        except bitstruct.Error:
            if self.priority > 7:
                raise Error('Expected priority 0..7, but got {}.'.format(self.priority))
            elif self.reserved > 1:
                raise Error('Expected reserved 0..1, but got {}.'.format(self.reserved))
            elif self.data_page > 1:
                raise Error('Expected data page 0..1, but got {}.'.format(self.data_page))
            elif self.pdu_format > 255:
                raise Error('Expected PDU format 0..255, but got {}.'.format(self.pdu_format))
            elif self.pdu_specific > 255:
                raise Error('Expected PDU specific 0..255, but got {}.'.format(self.pdu_specific))
            elif self.source_address > 255:
                raise Error('Expected source address 0..255, but got {}.'.format(self.source_address))
            else:
                raise Error('Internal error.')

        return bitstruct.unpack('u29', packed)[0]

    @property
    def pgn(self):
        if self.pdu_format < 240 and self.pdu_specific != 0:
            raise Error(
                'Expected PDU specific 0 when PDU format is '
                '0..239, but got {}.'.format(self.pdu_specific))

        try:
            packed = bitstruct.pack(
                'u1u1u8u8', self.reserved, self.data_page,
                self.pdu_format, self.pdu_specific)
        except bitstruct.Error:
            if self.reserved > 1:
                raise Error('Expected reserved 0..1, but got {}.'.format(self.reserved))
            elif self.data_page > 1:
                raise Error('Expected data page 0..1, but got {}.'.format(self.data_page))
            elif self.pdu_format > 255:
                raise Error('Expected PDU format 0..255, but got {}.'.format(self.pdu_format))
            elif self.pdu_specific > 255:
                raise Error('Expected PDU specific 0..255, but got {}.'.format(self.pdu_specific))
            else:
                raise Error('Internal error.')

        return bitstruct.unpack('u18', packed)[0]

    def __eq__(self, other):
        if isinstance(other, int):
            try:
                other = self.from_frame_id(other)
            except Error:
                return False

            return other == self
        elif isinstance(other, J1939FrameId):
            return other.frame_id == self.frame_id

        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __int__(self):
        return self.frame_id

    def __str__(self):
        return str(int(self))
