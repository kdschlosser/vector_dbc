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


class ECU(object):
    """
    An ECU is the physical representation of a node or a group of nodes.

    This is a way of organizing a module or device that has more then one node address.
    An Example would be thea PCM (Powertrain Control Module) in a vebicle,
    a PCM is an ECM (Engine Control Module), TCM (Transmission Control Module) and possibly
    others housed into a single physical unit. A node would represent the ECM or the TCM.

    This has no other purpose other then organization.

    To define an ecm you use the `ecm` property in a `Node` instance.
    """

    def __init__(self, database, name):
        self._database = database
        self._name = name

    @property
    def nodes(self):
        return [
            node for node in self._database.nodes
            if node.ecu is not None and node.ecu == self.name
        ]

    @property
    def database(self):
        return self._database

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        nodes = self.nodes
        self._name = value

        for node in nodes:
            node.ecu = self

    def __str__(self):
        return self._name

    def __eq__(self, other):
        if isinstance(other, bytes):
            other = other.decode('utf-8')

        if isinstance(other, str):
            return other == self._name

        if isinstance(other, ECU):
            return other.name == self._name

        return False

    def __ne__(self, other):
        return not self.__eq__(other)


