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

import logging

from . import dbc
from .internal_database import InternalDatabase
from . import attribute
from .frame_id import (
    FrameId,
    J1939FrameId,
    GMParameterId,
    GMParameterIdExtended
)

FRAME_IDS = (
    FrameId,
    J1939FrameId,
    GMParameterId,
    GMParameterIdExtended
)

LOGGER = logging.getLogger(__name__)


class Database(attribute.AttributeMixin):
    _marker = ''
    """
    This class contains all messages, signals and definitions of a CAN
    network.

    The factory functions :func:`load()<cantools.database.load()>`,
    :func:`load_file()<cantools.database.load_file()>` and
    :func:`load_string()<cantools.database.load_string()>` returns
    instances of this class.

    If `strict` is ``True`` an exception is raised if any signals are
    overlapping or if they don't fit in their message.
    """

    def __init__(
        self, messages=None, nodes=None, buses=None, version=None,
        dbc_specifics=None, frame_id_mask=None, strict=True
    ):
        self._messages = messages if messages else []
        self._nodes = nodes if nodes else []
        self._buses = buses if buses else []
        self._name_to_message = {}
        self._frame_id_to_message = {}
        self._version = version
        self._dbc = dbc_specifics

        if frame_id_mask is None:
            frame_id_mask = 0xffffffff

        self._frame_id_mask = frame_id_mask
        self._strict = strict
        self.refresh()

    @property
    def messages(self):
        """
        A list of messages in the database.

        Use :meth:`.get_message_by_frame_id()` or
        :meth:`.get_message_by_name()` to find a message by its frame
        id or name.
        """
        return self._messages

    @messages.setter
    def messages(self, value):
        for message in value:
            res = self._add_message(message)
            if res is True:
                self._messages += [message]
            else:
                self._messages.remove(res)
                self._messages += [message]

            message._parent = self
            message.refresh(self._strict)

    @property
    def nodes(self):
        """A list of nodes in the database."""
        return self._nodes

    @nodes.setter
    def nodes(self, value):
        node_names = {node.name: node for node in self._nodes}

        for node in value:
            if node.name in node_names:
                LOGGER.warning(
                    "Overwriting node '%s'",
                    node.name
                )

                index = self._nodes.index(node_names[node.name])
                self._nodes[index] = node
            else:
                self._nodes += [node]

    @property
    def buses(self):
        """A list of CAN buses in the database."""
        return self._buses

    @property
    def version(self):
        """The database version, or ``None`` if unavailable."""
        return self._version

    @version.setter
    def version(self, value):
        self._version = value

    @property
    def dbc(self):
        """An object containing dbc specific properties like e.g. attributes."""
        return self._dbc

    @dbc.setter
    def dbc(self, value):
        self._dbc = value

    @classmethod
    def load(cls, path):
        instance = cls()

        # noinspection PyArgumentEqualDefault
        with open(path, 'r', encoding='cp1252') as f:
            instance.add_string(f.read())

        return instance

    def add_file(self, filename, encoding='cp1252'):
        """
        Open, read and parse DBC data from given file and add the parsed
        data to the database.

        `encoding` specifies the file encoding.
        """
        # noinspection PyArgumentEqualDefault
        with open(filename, 'r', encoding=encoding) as fin:
            self.add_string(fin.read())

    def add_string(self, string):
        """Parse given DBC data string and add the parsed data to the database."""
        database = dbc.load_string(self, string, self._strict)

        self._messages += database.messages
        self._nodes = database.nodes
        self._buses = database.buses
        self._version = database.version
        self._dbc = database.dbc
        self.refresh()

    def _add_message(self, message):
        """Add given message to the database."""
        res = True

        if message.name in self._name_to_message:
            LOGGER.warning(
                "Overwriting message '%s' with '%s' in the "
                "name to message dictionary.",
                self._name_to_message[message.name].name,
                message.name)

            res = self._name_to_message[message.name]

        masked_frame_id = (message.frame_id.frame_id & self._frame_id_mask)

        if masked_frame_id in self._frame_id_to_message:
            LOGGER.warning(
                "Overwriting message '%s' with '%s' in the frame id to message "
                "dictionary because they have identical masked frame ids 0x%x.",
                self._frame_id_to_message[masked_frame_id].name,
                message.name,
                masked_frame_id)

            res = self._frame_id_to_message[masked_frame_id]

        self._name_to_message[message.name] = message
        self._frame_id_to_message[masked_frame_id] = message
        return res

    def as_string(self):
        """Return the database as a string formatted as a DBC file."""
        return dbc.dump_string(InternalDatabase(
            self._messages, self._nodes,
            self._buses, self._version, self._dbc))

    def get_message(self, frame_id_or_name):
        """Find the message object for given frame id `frame_id`."""
        if isinstance(frame_id_or_name, (str, bytes)):
            if isinstance(frame_id_or_name, bytes):
                frame_id_or_name = frame_id_or_name.decode('utf-8')

            if frame_id_or_name in self._name_to_message:
                res = [self._name_to_message[frame_id_or_name]]
            else:
                res = []
        else:
            res = [
                message for message in self.messages
                if message.frame_id == frame_id_or_name
            ]

        if len(res) > 0:
            return res[0]

        raise KeyError(frame_id_or_name)

    def get_node(self, name_or_id):
        """Find the node object for given name `name`."""

        if isinstance(name_or_id, int):
            res = [
                node for node in self._nodes
                if name_or_id in (node.tp_rx_indentfier, node.tp_tx_indentfier)
            ]

        else:
            res = [
                node for node in self._nodes
                if node.name == name_or_id
            ]

        if len(res) > 0:
            return res[0]

        raise KeyError(name_or_id)

    def get_bus(self, name):
        """Find the bus object for given name `name`."""

        bus = [bus for bus in self._buses if bus.name == name]
        if len(bus) > 0:
            return bus[0]

        raise KeyError(name)

    def encode_message(
        self, frame_id_or_name, data, scaling=True,
        padding=False, strict=True
    ):
        """
        Encode given signal data `data` as a message of given frame id or
        name `frame_id_or_name`. `data` is a dictionary of signal
        name-value entries.

        If `scaling` is ``False`` no scaling of signals is performed.

        If `padding` is ``True`` unused bits are encoded as 1.

        If `strict` is ``True`` all signal values must be within their
        allowed ranges, or an exception is raised.
        """
        message = self.get_message(frame_id_or_name)
        return message.encode(data, scaling, padding, strict)

    def decode_message(
        self, frame_id_or_name, data,
        decode_choices=True, scaling=True
    ):
        """
        Decode given signal data `data` as a message of given frame id or
        name `frame_id_or_name`. Returns a dictionary of signal
        name-value entries.

        If `decode_choices` is ``False`` scaled values are not
        converted to choice strings (if available).

        If `scaling` is ``False`` no scaling of signals is performed.
        """
        message = self.get_message(frame_id_or_name)
        return message.decode(data, decode_choices, scaling)

    def refresh(self):
        """
        Refresh the internal database state.

        This method must be called after modifying any message in the
        database to refresh the internal lookup tables used when
        encoding and decoding messages.
        """
        self._name_to_message = {}
        self._frame_id_to_message = {}

        for message in self._messages:
            message._parent = self
            message.refresh(self._strict)
            self._add_message(message)

        for node in self._nodes:
            node._parent = self

        for bus in self._buses:
            bus._parent = self

    @property
    def nm_base_address(self):
        """
        Defines the CAN ID of the first network management message.
        """
        return self._get_attribute('NmBaseAddress')

    @nm_base_address.setter
    def nm_base_address(self, value):
        self._set_hex_attribute('NmBaseAddress', 0x0, 0x7FF, value)

    @property
    def tp_base_address(self):
        """
        The base address that is used to determine the CAN ID for the TP messages (extended addressing mode only).
        """
        return self._get_attribute('TpBaseAddress')

    @tp_base_address.setter
    def tp_base_address(self, value):
        self._set_hex_attribute('TpBaseAddress', 0x0, 0x7FF, value)

    @property
    def use_gm_parameter_ids(self):
        """
        GM parameter ids derived from the frame id.
        """
        return bool(self._get_attribute('UseGMParameterIDs'))

    @use_gm_parameter_ids.setter
    def use_gm_parameter_ids(self, value):
        self._set_int_attribute('UseGMParameterIDs', 0, 1, int(value))

    @property
    def gen_nwm_sleep_time(self):
        """
        If all nodes have the same wait time up to SleepRequest, set this time in this attribute in ms.
        """
        return self._get_attribute('GenNWMSleepTime')

    @gen_nwm_sleep_time.setter
    def gen_nwm_sleep_time(self, value):
        self._set_int_attribute('GenNWMSleepTime', 0, 2147483647, value)

    @property
    def nm_message_count(self):
        """
        Defines the number of CAN IDs used or reserved for network management messages.

        This is then the maximum number of network management message on the network.
        """
        return self._get_attribute('NmMessageCount')

    @nm_message_count.setter
    def nm_message_count(self, value):
        self._set_int_attribute('NmMessageCount', 1, 255, value)

    @property
    def version_year(self):
        """
        Specifies the year of the network release.
        """
        return self._get_attribute('VersionYear')

    @version_year.setter
    def version_year(self, value):
        self._set_int_attribute('VersionYear', 0, 99, value)

    @property
    def version_month(self):
        """
        Specifies the month of the network release.
        """
        return self._get_attribute('VersionMonth')

    @version_month.setter
    def version_month(self, value):
        self._set_int_attribute('VersionMonth', 1, 12, value)

    @property
    def version_week(self):
        """
        Specifies the week of the network release.
        """
        return self._get_attribute('VersionWeek')

    @version_week.setter
    def version_week(self, value):
        self._set_int_attribute('VersionWeek', 0, 52, value)

    @property
    def version_day(self):
        """
        Specifies the day of the network release.
        """
        return self._get_attribute('VersionDay')

    @version_day.setter
    def version_day(self, value):
        self._set_int_attribute('VersionDay', 1, 31, value)

    @property
    def version_number(self):
        """
        Specifies the version number of the network release. The numbers have to be given in BCD coding.
        """
        return self._get_attribute('VersionNumber')

    @version_number.setter
    def version_number(self, value):
        self._set_int_attribute('VersionNumber', 0, 2147483647, value)

    @property
    def nm_type(self):
        """
        Defines the type of network management used on the network e.g. Vector.
        """
        return self._get_attribute('NmType')

    @nm_type.setter
    def nm_type(self, value):
        self._set_str_attribute('NmType', value)

    @property
    def manufacturer(self):
        """
        Specifies the OEM.
        """
        return self._get_attribute('Manufacturer')

    @manufacturer.setter
    def manufacturer(self, value):
        self._set_str_attribute('Manufacturer', value)

    @property
    def db_name(self):
        """
        Specifies the OEM.
        """
        return self._get_attribute('DBName')

    @db_name.setter
    def db_name(self, value):
        self._set_str_attribute('DBName', value)

    @property
    def bus_type(self):
        """
        Defines the type of the network, e.g. "CAN", "LIN", "MOST", "Ethernet", "ARINC425", "AFDX"
        """
        return self._get_attribute('BusType')

    @bus_type.setter
    def bus_type(self, value):
        self._set_str_attribute('BusType', value)

    @property
    def protocol_type(self):
        """
        This attribute defines the protocol type.

        Several functions are activated in CANoe/CANalyzer by this attribute.
        The appropriate option has to be installed and a license must be available.

        J1939, CANopen, AFDX, ARINC825, CANaerospace, CANopenSafety, Aerospace, NMEA2000

        """
        return self._get_attribute('ProtocolType')

    @protocol_type.setter
    def protocol_type(self, value):
        self._set_str_attribute('ProtocolType', value)

    @property
    def is_multiplex_ext_enabled(self):
        """
        The extended multiplexor concept allows you to define several multiplexor signals in
        a single message. One multiplexed signal may be multiplexed through several multiplex
        values. If you want to use extended multiplexing, you must activate the option Enable
        extended multiplexing on the Edit page of the Settings dialog. If the bus type is not
        Ethernet, ARINC425 or AFDX and if the protocol type does not have one of the values
        J1939, NMEA2000, ISO11783, CANopen, CANopenSafety or Aerospace, you must set the
        MultiplexExtEnabled attribute to Yes for the network.

        """
        return bool(self._get_attribute('MultiplexExtEnabled'))

    @is_multiplex_ext_enabled.setter
    def is_multiplex_ext_enabled(self, value):
        self._set_yes_no_attribute('MultiplexExtEnabled', value)

