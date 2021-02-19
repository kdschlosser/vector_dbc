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

from . import attribute
from . import attribute_definition
from . import ecu
from .comment import NodeComment
from .frame_id import (
    J1939FrameId,
    GMParameterIdExtended
)


class Node(attribute.AttributeMixin):
    """An NODE on the CAN bus."""

    _marker = 'BU_'

    def __init__(self, parent, name, comment, dbc_specifics=None):
        self._name = name
        self._comment = comment
        self._dbc = dbc_specifics
        self._parent = parent

    def encode(self, frame_id_or_name, data, scaling=True, padding=False, strict=True):
        message = self._parent.get_message(frame_id_or_name)

        if self not in message.senders:
            raise KeyError(frame_id_or_name)

        data = message.encode(data, scaling, padding, strict)
        data.set_sending_node(self)

        return data

    def decode(self, frame_id_or_name, data, decode_choices=True, scaling=True):
        if isinstance(frame_id_or_name, bytes):
            frame_id_or_name = frame_id_or_name.decode('utf-8')

        message = self._parent.get_message(frame_id_or_name)

        if self not in message.receivers:
            raise KeyError(frame_id_or_name)

        tp_tx_indentfier = self.tp_tx_indentfier

        if isinstance(frame_id_or_name, int):
            frame_id = message.frame_id.from_frame_id(frame_id_or_name)

        elif isinstance(frame_id_or_name, str):
            frame_id = message.frame_id

        else:
            frame_id = frame_id_or_name

        if tp_tx_indentfier is not None:
            if (
                (isinstance(frame_id, J1939FrameId) and frame_id.source_address != tp_tx_indentfier) or
                (isinstance(frame_id, GMParameterIdExtended) and frame_id.source_id != tp_tx_indentfier)
            ):
                raise KeyError(frame_id_or_name)

        data = message.decode(data, decode_choices, scaling)
        data.frame_id = frame_id

        return data

    @property
    def tx_signals(self):
        signals = [
            signal for message in self._parent.messages
            for signal in message.signals
            if self in message.senders
        ]
        return signals

    @property
    def rx_signals(self):
        signals = [
            signal for message in self._parent.messages
            for signal in message.signals
            if self in message.receivers
        ]
        return signals

    @property
    def database(self):
        return self._parent

    @property
    def name(self):
        """The node name as a string."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def comment(self):
        """The node comment, or ``None`` if unavailable."""
        if self._comment is not None and not isinstance(self._comment, NodeComment):
            self._comment = NodeComment(self._comment)
            self._comment.node = self

        return self._comment

    @comment.setter
    def comment(self, value):
        if value is not None and not isinstance(value, (str, NodeComment)):
            value = str(value)

        self._comment = value

    @property
    def dbc(self):
        """An object containing dbc specific properties like e.g. attributes."""
        return self._dbc

    @dbc.setter
    def dbc(self, value):
        self._dbc = value

    @property
    def nm_station_address(self):
        """
        Defines the NM address of the node.

        This address is used directly to compute the identifier of the associated Network Management message

        message ID = NmStationAddress + NmBaseAddress

        Example  Example

        NmStationAddress = 18, NmBaseAddress = 0x400
        => message ID = 0x412
        """
        return self._get_attribute('NmStationAddress')

    @nm_station_address.setter
    def nm_station_address(self, value):
        self._set_hex_attribute('NmStationAddress', 0, 2147483647, value)

    @property
    def nm_j1939_aac(self):
        return self._get_attribute('NmJ1939AAC')

    @nm_j1939_aac.setter
    def nm_j1939_aac(self, value):
        self._set_int_attribute('NmJ1939AAC', 0, 1, value)

    @property
    def nm_j1939_industry_group(self):
        return self._get_attribute('NmJ1939IndustryGroup')

    @nm_j1939_industry_group.setter
    def nm_j1939_industry_group(self, value):
        self._set_int_attribute('NmJ1939IndustryGroup', 0, 7, value)

    @property
    def nm_j1939_system(self):
        return self._get_attribute('NmJ1939System')

    @nm_j1939_system.setter
    def nm_j1939_system(self, value):
        self._set_int_attribute('NmJ1939System', 0, 127, value)

    @property
    def nm_j1939_system_instance(self):
        return self._get_attribute('NmJ1939SystemInstance')

    @nm_j1939_system_instance.setter
    def nm_j1939_system_instance(self, value):
        self._set_int_attribute('NmJ1939SystemInstance', 0, 15, value)

    @property
    def nm_j1939_function(self):
        return self._get_attribute('NmJ1939Function')

    @nm_j1939_function.setter
    def nm_j1939_function(self, value):
        self._set_int_attribute('NmJ1939Function', 0, 255, value)

    @property
    def nm_j1939_function_instance(self):
        return self._get_attribute('NmJ1939FunctionInstance')

    @nm_j1939_function_instance.setter
    def nm_j1939_function_instance(self, value):
        self._set_int_attribute('NmJ1939FunctionInstance', 0, 7, value)

    @property
    def nm_j1939_ecu_instance(self):
        return self._get_attribute('NmJ1939ECUInstance')

    @nm_j1939_ecu_instance.setter
    def nm_j1939_ecu_instance(self, value):
        self._set_int_attribute('NmJ1939ECUInstance', 0, 3, value)

    @property
    def nm_j1939_manufacturer_code(self):
        return self._get_attribute('NmJ1939ManufacturerCode')

    @nm_j1939_manufacturer_code.setter
    def nm_j1939_manufacturer_code(self, value):
        self._set_int_attribute('NmJ1939ManufacturerCode', 0, 2047, value)

    @property
    def nm_j1939_identity_number(self):
        return self._get_attribute('NmJ1939IdentityNumber')

    @nm_j1939_identity_number.setter
    def nm_j1939_identity_number(self, value):
        self._set_int_attribute('NmJ1939IdentityNumber', 0, 2097151, value)

    @property
    def nm_can(self):
        """
        Specifies the CAN channel (1 or 2) on which the NM should send and receive.

        Note that this attribute is only taken into consideration in older versions of
        CANoe or if the "compatible" mode of a newer version is used.
        """
        return self._get_attribute('NmCAN')

    @nm_can.setter
    def nm_can(self, value):
        self._set_int_attribute('NmCAN', 1, 2, value)

    @property
    def gen_node_sleep_time(self):
        """
        If the nodes have different wait times up to SleepRequest,
        set the time in this attribute in ms for each node.

        As soon as the attribute has a value>0, GenNWMSleepTime is not evaluated for this node.
        """
        return self._get_attribute('GenNodSleepTime')

    @gen_node_sleep_time.setter
    def gen_node_sleep_time(self, value):
        self._set_int_attribute('GenNodSleepTime', 0, 2147483647, value)

    @property
    def nm_node(self):
        """Defines whether the node participates in the network management or not."""
        if 'NmNode' in self.dbc.attributes:
            value = self.dbc.attributes['NmNode'].value
            return bool(value)

    @nm_node.setter
    def nm_node(self, value):
        self._set_yes_no_attribute('NmNode', value)

    @property
    def tp_node_base_address(self):
        """The base address that is used to determine the CAN ID for the TP messages (extended addressing mode only)."""
        return self._get_attribute('TpNodeBaseAddress')

    @tp_node_base_address.setter
    def tp_node_base_address(self, value):
        self._set_hex_attribute('TpNodeBaseAddress', 0x0, 0x7FF, value)

    @property
    def tp_tx_indentfier(self):
        """Transmit ID for normal and 11 bit mixed addressing."""
        return self._get_attribute('TpTxIdentifier')

    @tp_tx_indentfier.setter
    def tp_tx_indentfier(self, value):
        self._set_hex_attribute('TpTxIdentifier', 0x0, 0x7FFFFFF, value)

    @property
    def tp_rx_indentfier(self):
        """Receive ID for normal and 11 bit mixed addressing."""
        return self._get_attribute('TpRxIdentifier')

    @tp_rx_indentfier.setter
    def tp_rx_indentfier(self, value):
        self._set_hex_attribute('TpRxIdentifier', 0x0, 0x7FFFFFF, value)

    @property
    def tp_rx_mask(self):
        """Identifies the receive message."""
        return self._get_attribute('TpRxMask')

    @tp_rx_mask.setter
    def tp_rx_mask(self, value):
        self._set_hex_attribute('TpRxMask', 0x0, 0x7FF, value)

    @property
    def tp_can_bus(self):
        """Identifies the CAN channel used."""
        return self._get_attribute('TpCanBus')

    @tp_can_bus.setter
    def tp_can_bus(self, value):
        self._set_int_attribute('TpCanBus', 1, 2, value)

    @property
    def tp_tx_adr_mode(self):
        """
        Defines whether the node uses physical (0) or functional (1) addressing
        (for address modes normal fixed and mixed).
        """
        return self._get_attribute('TpTxAdrMode')

    @tp_tx_adr_mode.setter
    def tp_tx_adr_mode(self, value):
        self._set_int_attribute('TpTxAdrMode', 0, 1, value)

    @property
    def tp_address_extension(self):
        """Sets the address extension used for (11 bit) mixed addressing mode."""
        return self._get_attribute('TpAddressExtension')

    @tp_address_extension.setter
    def tp_address_extension(self, value):
        self._set_int_attribute('TpAddressExtension', 0, 2147483647, value)

    @property
    def tp_st_min(self):
        """
        Minimum Separation Time required for this node.

        This is the minimum time the node shall wait between the transmissions of two consecutive frames.
        """
        return self._get_attribute('TpSTMin')

    @tp_st_min.setter
    def tp_st_min(self, value):
        self._set_int_attribute('TpSTMin', 0, 2147483647, value)

    @property
    def tp_block_size(self):
        """Block size for this node."""
        return self._get_attribute('TpBlockSize')

    @tp_block_size.setter
    def tp_block_size(self, value):
        self._set_int_attribute('TpBlockSize', 0, 2147483647, value)

    @property
    def tp_addressing_mode(self):
        """
        Defines the nodes addressing mode

        0 (normal addressing),
        1 (extended addressing),
        2 (normal fixed addressing),
        3 (mixed addressing),
        4 (11 bit mixed addressing)
        """
        return self._get_attribute('TpAddressingMode')

    @tp_addressing_mode.setter
    def tp_addressing_mode(self, value):
        self._set_int_attribute('TpAddressingMode', 0, 4, value)

    @property
    def tp_target_address(self):
        """This attribute is relevant for extended addressing only. It specifies the nodes target address."""
        return self._get_attribute('TpTargetAddress')

    @tp_target_address.setter
    def tp_target_address(self, value):
        self._set_hex_attribute('TpTargetAddress', 0x0, 0xFF, value)

    @property
    def tp_use_fc(self):
        """
        Indicates whether flow control messages should be used (1) or not (0).

        The flow control mechanism allows the receiver to inform the sender about the receivers capabilities.
        """
        return self._get_attribute('TpUseFC')

    @tp_use_fc.setter
    def tp_use_fc(self, value):
        self._set_int_attribute('TpUseFC', 0, 1, value)

    @property
    def diag_station_address(self):
        """Specifies the nodes diagnostic address."""
        return self._get_attribute('DiagStationAddress')

    @diag_station_address.setter
    def diag_station_address(self, value):
        self._set_hex_attribute('DiagStationAddress', 0x0, 0xFF, value)

    @property
    def node_layer_modules(self):
        """
        List of node layer DLLs loaded in CANoe.

        The node layer modules are separated in the string with a comma (",")
        e.g. "OSEK_TP.DLL, OSEKNM.DLL".
        """
        return self._get_attribute('NodeLayerModules')

    @node_layer_modules.setter
    def node_layer_modules(self, value):
        self._set_str_attribute('NodeLayerModules', value)

    @property
    def ecu(self):
        """
        Specifies the name of the ECU the node belongs to.

        This attribute is only needed if an ECU contains several nodes
        (e.g. to define interfaces to multiple buses).
        """
        res = self._get_attribute('ECU')
        if res is not None:
            res = ecu.ECU(self._parent, res)

        return res

    @ecu.setter
    def ecu(self, value):
        if isinstance(value, ecu.ECU):
            value = value.name

        self._set_str_attribute('ECU', value)

    @property
    def canoe_start_delay(self):
        """
        Time span after the start of measurement

         Which the particular node remains completely passive.
         It does not react to external influences, nor does it activate itself.
         It does not change its behavior and function like every other node until the time span has elapsed.
         """
        return self._get_attribute('CANoeStartDelay')

    @canoe_start_delay.setter
    def canoe_start_delay(self, value):
        self._set_int_attribute('CANoeStartDelay', 0, 2147483647, value)

    @property
    def canoe_drift(self):
        """Percentage the timers used in the node are lengthened or shortened."""
        return self._get_attribute('CANoeDrift')

    @canoe_drift.setter
    def canoe_drift(self, value):
        self._set_int_attribute('CANoeDrift', 0, 2147483647, value)

    @property
    def canoe_jitter_min(self):
        """
        With CANoeJitterMin and CANOeJitterMax the user specifies the interval within
        which the fluctuation of the timers of the node should lie. The fluctuation is
        uniformly distributed.
        """
        return self._get_attribute('CANoeJitterMin')

    @canoe_jitter_min.setter
    def canoe_jitter_min(self, value):
        self._set_int_attribute('CANoeJitterMin', 0, 2147483647, value)

    @property
    def canoe_jitter_max(self):
        """
        With CANoeJitterMin and CANOeJitterMax the user specifies the interval within
        which the fluctuation of the timers of the node should lie. The fluctuation is
        uniformly distributed.
        """
        return self._get_attribute('CANoeJitterMax')

    @canoe_jitter_max.setter
    def canoe_jitter_max(self, value):
        self._set_int_attribute('CANoeJitterMax', 0, 2147483647, value)

    @property
    def il_used(self):
        """Set to Yes if the node uses an interaction layer."""
        if 'ILUsed' in self.dbc.attributes:
            value = self.dbc.attributes['ILUsed'].value
            return bool(value)

    @il_used.setter
    def il_used(self, value):

        if 'ILUsed' in self.dbc.attributes:
            self.dbc.attributes['ILUsed'].value = value
        else:

            if 'ILUsed' in self.dbc.attribute_definitions:
                definition = self.dbc.attribute_definitions['ILUsed']
            else:

                definition = attribute_definition.AttributeDefinition(
                    'ILUsed',
                    default_value=0,
                    kind='BU_',
                    type_name='ENUM',
                    choices={0: 'No', 1: 'Yes'}
                )

            self.dbc.attributes['ILUsed'] = attribute.Attribute(int(value), definition)

    @property
    def gen_nod_auto_gen_dsp(self):
        if 'GenNodAutoGenDsp' in self.dbc.attributes:
            value = self.dbc.attributes['GenNodAutoGenDsp'].value
            return bool(value)

    @gen_nod_auto_gen_dsp.setter
    def gen_nod_auto_gen_dsp(self, value):
        if 'GenNodAutoGenDsp' in self.dbc.attributes:
            self.dbc.attributes['GenNodAutoGenDsp'].value = value
        else:

            if 'GenNodAutoGenDsp' in self.dbc.attribute_definitions:
                definition = self.dbc.attribute_definitions['GenNodAutoGenDsp']
            else:

                definition = attribute_definition.AttributeDefinition(
                    'GenNodAutoGenDsp',
                    default_value=0,
                    kind='BU__',
                    type_name='ENUM',
                    choices={0: 'No', 1: 'Yes'}
                )

            self.dbc.attributes['GenNodAutoGenDsp'] = attribute.Attribute(int(value), definition)

    @property
    def gen_nod_auto_gen_snd(self):
        if 'GenNodAutoGenSnd' in self.dbc.attributes:
            value = self.dbc.attributes['GenNodAutoGenSnd'].value
            return bool(value)

    @gen_nod_auto_gen_snd.setter
    def gen_nod_auto_gen_snd(self, value):

        if 'GenNodAutoGenSnd' in self.dbc.attributes:
            self.dbc.attributes['GenNodAutoGenSnd'].value = value
        else:

            if 'GenNodAutoGenSnd' in self.dbc.attribute_definitions:
                definition = self.dbc.attribute_definitions['GenNodAutoGenSnd']
            else:

                definition = attribute_definition.AttributeDefinition(
                    'GenNodAutoGenSnd',
                    default_value=0,
                    kind='BU__',
                    type_name='ENUM',
                    choices={0: 'No', 1: 'Yes'}
                )

            self.dbc.attributes['GenNodAutoGenSnd'] = attribute.Attribute(int(value), definition)

    @property
    def gen_nod_nod_sleep_time(self):
        return self._get_attribute('GenNodSleepTime')

    @gen_nod_nod_sleep_time.setter
    def gen_nod_nod_sleep_time(self, value):
        self._set_int_attribute('GenNodSleepTime', 0, 2147483647, value)
