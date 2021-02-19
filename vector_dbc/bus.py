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
from .comment import Comment


class Bus(object):
    """A CAN bus."""

    def __init__(self, name, comment=None, baudrate=None):
        self._name = name
        self._comment = comment
        self._baudrate = baudrate
        self._parent = None

    @property
    def parent(self):
        return self._parent

    @property
    def name(self):
        """The bus name as a string."""
        return self._name

    @property
    def comment(self):
        """The bus comment, or ``None`` if unavailable."""
        if self._comment is not None and not isinstance(self._comment, Comment):
            self._comment = Comment(self._comment)

        return self._comment

    @comment.setter
    def comment(self, value):
        if value is not None and not isinstance(value, (str, Comment)):
            value = str(value)

        self._comment = value

    @property
    def baudrate(self):
        """The bus baudrate, or ``None`` if unavailable."""
        return self._baudrate
