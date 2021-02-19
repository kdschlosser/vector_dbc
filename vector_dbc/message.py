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

import binascii
from copy import deepcopy
from typing import Union

from .utils import format_or
from .utils import start_bit
from .utils import encode_data
from .utils import decode_data
from .utils import create_encode_decode_formats
from .errors import Error
from .errors import EncodeError
from .errors import DecodeError
from .frame_id import J1939FrameId, GMParameterId, FrameId, GMParameterIdExtended
from . import attribute
from . import attribute_definition
from . import can_data
from .comment import MessageComment


class Message(attribute.AttributeMixin):
    """
    A CAN message with frame id, comment, signals and other
    information.

    If `strict` is ``True`` an exception is raised if any signals are
    overlapping or if they don't fit in the message.
    """

    _marker = 'BO_'

    def __init__(
        self, parent, frame_id, name, length, signals=None, comment=None, senders=None,
        dbc_specifics=None, is_extended_frame=False, signal_groups=None, strict=True
    ):
        frame_id_bit_length = frame_id.bit_length()

        if is_extended_frame:
            if frame_id_bit_length > 29:
                raise Error(
                    'Extended frame id 0x{:x} is more than 29 bits in '
                    'message {}.'.format(frame_id, name))
        elif frame_id_bit_length > 11:
            raise Error(
                'Standard frame id 0x{:x} is more than 11 bits in '
                'message {}.'.format(frame_id, name))

        self._frame_id = frame_id
        self._is_extended_frame = is_extended_frame
        self._name = name
        self._length = length
        self._signals = signals if signals else []

        # if the 'comment' argument is a string, we assume that is an
        # english comment. this is slightly hacky because the
        # function's behavior depends on the type of the passed
        # argument, but it is quite convenient...
        if isinstance(comment, str):
            # use the first comment in the dictionary as "The" comment
            self._comments = {None: comment}
        elif comment is None:
            self._comments = {}
        else:
            # multi-lingual dictionary
            self._comments = comment

        self._senders = senders if senders else []
        self._dbc = dbc_specifics
        self._signal_groups = signal_groups
        self._codecs = None
        self._signal_tree = None
        self._strict = strict
        self._parent = parent
        self.refresh()

    @property
    def database(self):
        return self._parent

    def _create_codec(self, parent_signal=None, multiplexer_id=None):
        """Create a codec of all signals with given parent signal. This is a recursive function."""
        signals = []
        multiplexers = {}

        # Find all signals matching given parent signal name and given
        # multiplexer id. Root signals' parent and multiplexer id are
        # both None.
        for signal in self._signals:
            if signal.multiplexer_signal != parent_signal:
                continue

            if (
                multiplexer_id is not None and
                multiplexer_id not in signal.multiplexer_ids
            ):
                continue

            if signal.is_multiplexer:
                children_ids = set()

                for s in self._signals:
                    if s.multiplexer_signal != signal.name:
                        continue

                    children_ids.update(s.multiplexer_ids)

                # Some CAN messages will have muxes containing only
                # the multiplexer and no additional signals. At Tesla
                # these are indicated in advance by assigning them an
                # enumeration. Here we ensure that any named
                # multiplexer is included, even if it has no child
                # signals.
                if signal.choices:
                    children_ids.update(signal.choices.keys())

                for child_id in children_ids:
                    codec = self._create_codec(signal.name, child_id)

                    if signal.name not in multiplexers:
                        multiplexers[signal.name] = {}

                    multiplexers[signal.name][child_id] = codec

            signals.append(signal)

        return {
            'signals': signals,
            'formats': create_encode_decode_formats(signals, self._length),
            'multiplexers': multiplexers
        }

    def _create_signal_tree(self, codec):
        """Create a multiplexing tree node of given codec. This is a recursive function."""
        nodes = []

        for signal in codec['signals']:
            multiplexers = codec['multiplexers']

            if signal.name in multiplexers:
                node = {
                    signal.name: {
                        mux: self._create_signal_tree(mux_codec)
                        for mux, mux_codec in multiplexers[signal.name].items()
                    }
                }
            else:
                node = signal.name

            nodes.append(node)

        return nodes

    @property
    def frame_id(self) -> Union[FrameId, J1939FrameId, GMParameterId, GMParameterIdExtended]:
        """The message frame id."""
        if isinstance(self._frame_id, int):
            if self.database.use_gm_parameter_ids:
                if self._is_extended_frame:
                    self._frame_id = GMParameterIdExtended.from_frame_id(self._frame_id)
                else:
                    self._frame_id = GMParameterId.from_frame_id(self._frame_id)

            elif (
                self.database.protocol_type is not None and
                self.database.protocol_type == 'J1939'
            ):
                self._frame_id = J1939FrameId.from_frame_id(self._frame_id)

            else:
                self._frame_id = FrameId(self._frame_id)

        return self._frame_id

    @frame_id.setter
    def frame_id(self, value):
        self._frame_id = value

    @property
    def is_extended_frame(self):
        """``True`` if the message is an extended frame, ``False`` otherwise."""
        return self._is_extended_frame

    @is_extended_frame.setter
    def is_extended_frame(self, value):
        self._is_extended_frame = value

    @property
    def name(self):
        """The message name as a string."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def length(self):
        """The message data length in bytes."""
        return self._length

    @length.setter
    def length(self, value):
        self._length = value

    @property
    def signals(self):
        """A list of all signals in the message."""
        return self._signals

    @property
    def signal_groups(self):
        """A list of all signal groups in the message."""
        return self._signal_groups

    @signal_groups.setter
    def signal_groups(self, value):
        self._signal_groups = value

    @property
    def comments(self):
        """The dictionary with the descriptions of the signal in multiple languages. ``None`` if unavailable."""

        for key, val in list(self._comments.items())[:]:
            if val is not None:
                if isinstance(val, bytes):
                    val = val.decode('utf-8')
                if not isinstance(val, MessageComment):
                    val = MessageComment(val)
                    val.message = self

                self._comments[key] = val

        return self._comments

    @comments.setter
    def comments(self, value):
        if value is None:
            value = {}

        if not isinstance(value, dict):
            raise TypeError('passed value is not a dictionary `dict`')

        for key, val in list(value.items())[:]:
            if val is not None:
                if isinstance(val, bytes):
                    val = val.decode('utf-8')
                if not isinstance(val, (str, MessageComment)):
                    val = str(val)

                value[key] = val

        self._comments = value

    @property
    def comment(self):
        """
        The signal comment, or ``None`` if unavailable.

        Note that we implicitly try to return the comment's language
        to be English comment if multiple languages were specified.
        """
        comment = self._comments.get(None, None)

        if comment is None:
            comment = self._comments.get('EN', None)

            if comment is not None:
                if isinstance(comment, bytes):
                    comment = comment.decode('utf-8')

                if not isinstance(comment, MessageComment):
                    comment = MessageComment(comment)
                    comment.message = self
                    self._comments['EN'] = comment

        else:
            if isinstance(comment, bytes):
                comment = comment.decode('utf-8')

            if not isinstance(comment, MessageComment):
                comment = MessageComment(comment)
                comment.message = self
                self._comments[None] = comment

        return comment

    @comment.setter
    def comment(self, value):
        if isinstance(value, bytes):
            value = value.decode('utf-8')

        if value is not None and not isinstance(value, (str, MessageComment)):
            value = str(value)

        self._comments = {None: value}

    @property
    def senders(self):
        """A list of all sender nodes of this message."""
        senders = [node for node in self.database.nodes if node.name in self._senders]
        return senders

    @property
    def receivers(self):
        """A list of all receiver nodes attached to signals in this message"""
        receivers = set()
        for signal in self.signals:
            for receiver in signal.receivers:
                receivers.add(receiver)

        return [node for node in self.database.nodes if node.name in receivers]

    @property
    def dbc(self):
        """An object containing dbc specific properties like e.g. attributes."""
        return self._dbc

    @dbc.setter
    def dbc(self, value):
        self._dbc = value

    @property
    def signal_tree(self):
        """
        All signal names and multiplexer ids as a tree.

        Multiplexer signals are dictionaries, while other signals are strings.
        """
        return self._signal_tree

    def _get_mux_number(self, decoded, signal_name):
        mux = decoded[signal_name]

        if isinstance(mux, str):
            signal = self.get_signal_by_name(signal_name)
            mux = signal.choice_string_to_number(mux)

        return mux

    def _check_signals_ranges_scaling(self, signals, data):
        for signal in signals:
            value = data[signal.name]

            # Choices are checked later.
            if isinstance(value, str):
                continue

            if signal.minimum is not None and value < signal.minimum:
                raise EncodeError(
                    "Expected signal '{}' value greater than or equal to "
                    "{} in message '{}', but got {}.".format(
                        signal.name, signal.minimum, self._name, value))

            if signal.maximum is not None and value > signal.maximum:
                raise EncodeError(
                    "Expected signal '{}' value less than or equal to "
                    "{} in message '{}', but got {}.".format(
                        signal.name, signal.maximum, self.name, value))

    def _check_signals(self, signals, data, scaling):
        for signal in signals:
            if signal.name not in data:
                if signal.gen_sig_start_value is not None:
                    data[signal.name] = signal.gen_sig_start_value + signal.offset
                else:
                    raise EncodeError(
                        "Expected signal value for '{}' in data, but "
                        "got {}.".format(signal.name, data))

        if scaling:
            self._check_signals_ranges_scaling(signals, data)

    def _encode(self, node, data, scaling, strict):
        if strict:
            self._check_signals(node['signals'], data, scaling)

        encoded = encode_data(
            data, node['signals'], node['formats'], scaling)
        padding_mask = node['formats'].padding_mask
        multiplexers = node['multiplexers']

        for signal in multiplexers:
            mux = self._get_mux_number(data, signal)

            try:
                node = multiplexers[signal][mux]
            except KeyError:
                raise EncodeError(
                    'expected multiplexer id {}, but got '
                    '{}'.format(format_or(multiplexers[signal]), mux))

            mux_encoded, mux_padding_mask = self._encode(
                node, data, scaling, strict)
            encoded |= mux_encoded
            padding_mask &= mux_padding_mask

        return encoded, padding_mask

    def encode(self, data, scaling=True, padding=False, strict=True):
        """
        Encode given data as a message of this type.

        If `scaling` is ``False`` no scaling of signals is performed.

        If `padding` is ``True`` unused bits are encoded as 1.

        If `strict` is ``True`` all signal values must be within their
        allowed ranges, or an exception is raised.
        """

        encoded, padding_mask = self._encode(
            self._codecs, data, scaling, strict)

        if padding:
            encoded |= padding_mask

        encoded |= (0x80 << (8 * self._length))
        encoded = hex(encoded)[4:].rstrip('L')

        data = can_data.TXData(binascii.unhexlify(encoded)[:self._length])
        data.frame_id = self.frame_id

        return data

    def _decode(self, node, data, decode_choices, scaling):
        decoded = decode_data(
            data, node['signals'], node['formats'],
            decode_choices, scaling)

        multiplexers = node['multiplexers']

        for signal in multiplexers:
            mux = self._get_mux_number(decoded, signal)

            try:
                node = multiplexers[signal][mux]
            except KeyError:
                raise DecodeError(
                    'expected multiplexer id {}, but got '
                    '{}'.format(format_or(multiplexers[signal]), mux))

            decoded.update(self._decode(
                node, data, decode_choices, scaling))

        return decoded

    def decode(self, data, decode_choices=True, scaling=True):
        """
        Decode given data as a message of this type.

        If `decode_choices` is ``False`` scaled values are not
        converted to choice strings (if available).

        If `scaling` is ``False`` no scaling of signals is performed.
        """
        data = data[:self._length]
        data = can_data.RXData(
            self._decode(self._codecs, data, decode_choices, scaling)
        )
        data.frame_id = self.frame_id
        return data

    def get_signal_by_name(self, name):
        for signal in self._signals:
            if signal.name == name:
                return signal

        raise KeyError(name)

    def is_multiplexed(self):
        """Returns ``True`` if the message is multiplexed, otherwise ``False``."""
        return bool(self._codecs['multiplexers'])

    def _check_signal(self, message_bits, signal):
        signal_bits = signal.length * [signal.name]

        if signal.byte_order == 'big_endian':
            padding = start_bit(signal) * [None]
            signal_bits = padding + signal_bits
        else:
            signal_bits += signal.start * [None]

            if len(signal_bits) < len(message_bits):
                padding = (len(message_bits) - len(signal_bits)) * [None]
                reversed_signal_bits = padding + signal_bits
            else:
                reversed_signal_bits = signal_bits

            signal_bits = []

            for i in range(0, len(reversed_signal_bits), 8):
                signal_bits = reversed_signal_bits[i:i + 8] + signal_bits

        # Check that the signal fits in the message.
        if len(signal_bits) > len(message_bits):
            print(
                'The signal {} does not fit in message {}.'.format(
                    signal.name, self.name))
            return
            # raise Error(
            #     'The signal {} does not fit in message {}.'.format(
            #         signal.name,
            #         self.name))

        # Check that the signal does not overlap with other
        # signals.
        for offset, signal_bit in enumerate(signal_bits):
            if signal_bit is not None:
                if message_bits[offset] is not None:
                    print(
                        'The signals {} and {} are overlapping in message {}.'.format(
                            signal.name, message_bits[offset], self.name))

                    for i, name in enumerate(message_bits):
                        if name == signal_bit:
                            message_bits[i] = None

                    return

                message_bits[offset] = signal.name

    def _check_mux(self, message_bits, mux):
        signal_name, children = list(mux.items())[0]
        self._check_signal(
            message_bits, self.get_signal_by_name(signal_name))
        children_message_bits = deepcopy(message_bits)

        for multiplexer_id in sorted(children):
            child_tree = children[multiplexer_id]
            child_message_bits = deepcopy(children_message_bits)
            self._check_signal_tree(child_message_bits, child_tree)

            for i, child_bit in enumerate(child_message_bits):
                if child_bit is not None:
                    message_bits[i] = child_bit

    def _check_signal_tree(self, message_bits, signal_tree):
        for signal_name in signal_tree:
            if isinstance(signal_name, dict):
                self._check_mux(message_bits, signal_name)
            else:
                self._check_signal(
                    message_bits, self.get_signal_by_name(signal_name))

    def _check_signal_lengths(self):
        for signal in self._signals:
            if signal.length <= 0:
                raise Error(
                    'The signal {} length {} is not greater '
                    'than 0 in message {}.'.format(
                        signal.name, signal.length, self.name))

    def refresh(self, strict=None):
        """
        Refresh the internal message state.

        If `strict` is ``True`` an exception is raised if any signals
        are overlapping or if they don't fit in the message. This
        argument overrides the value of the same argument passed to
        the constructor.
        """
        self._signals.sort(key=start_bit)
        self._check_signal_lengths()
        self._codecs = self._create_codec()
        self._signal_tree = self._create_signal_tree(self._codecs)

        if strict is None:
            strict = self._strict

        if strict:
            message_bits = 8 * self.length * [None]
            self._check_signal_tree(message_bits, self.signal_tree)

        for signal in self._signals:
            signal._parent = self

        for signal_group in self._signal_groups:
            signal_group._parent = self

    @property
    def gen_msg_delay_time(self):
        """
        Defines the minimum time between two message transmissions.
        """
        return self._get_attribute('GenMsgDelayTime')

    @gen_msg_delay_time.setter
    def gen_msg_delay_time(self, value):
        self._set_int_attribute('GenMsgDelayTime', 0, 2147483647, value)

    @property
    def gen_msg_cycle_time(self):
        """
        Defines the fixed periodicity for cyclic message transmissions.
        """
        return self._get_attribute('GenMsgCycleTime')

    @gen_msg_cycle_time.setter
    def gen_msg_cycle_time(self, value):
        self._set_int_attribute('GenMsgCycleTime', 0, 2147483647, value)

    @property
    def gen_msg_cycle_time_fast(self):
        """
        Defines the periodicity for fast message transmissions.

        Messages are transmitted fast if one of the signals placed on the message is in an active state.
        """
        return self._get_attribute('GenMsgCycleTimeFast')

    @gen_msg_cycle_time_fast.setter
    def gen_msg_cycle_time_fast(self, value):
        self._set_int_attribute('GenMsgCycleTimeFast', 0, 2147483647, value)

    @property
    def gen_msg_cycle_time_active(self):
        """
        Same as GenMsgCycleTimeFast for the CAPL Generators interaction layer.
        """
        return self._get_attribute('GenMsgCycleTimeActive')

    @gen_msg_cycle_time_active.setter
    def gen_msg_cycle_time_active(self, value):
        self._set_int_attribute('GenMsgCycleTimeActive', 0, 2147483647, value)

    @property
    def gen_msg_start_delay_time(self):
        """
        Defines the delay after system start-up, the message is sent the first time.
        """
        return self._get_attribute('GenMsgStartDelayTime')

    @gen_msg_start_delay_time.setter
    def gen_msg_start_delay_time(self, value):
        self._set_int_attribute('GenMsgStartDelayTime', 0, 2147483647, value)

    @property
    def gen_msg_nr_of_repetition(self):
        """
        If the transmission of a message has to be repeated,
        this attribute defines the number how often it will be repeated.

        If a message transmission is repeated depends on the value of GenSigSendType
        of the signals placed on the message.
        """
        return self._get_attribute('GenMsgNrOfRepetition')

    @gen_msg_nr_of_repetition.setter
    def gen_msg_nr_of_repetition(self, value):
        self._set_int_attribute('GenMsgNrOfRepetition', 0, 2147483647, value)

    @property
    def gen_msg_fast_on_start(self):
        """
        Defines the time duration in milliseconds to send cyclic messages with a
        faster cycle time (GenMsgCycleTimeFast) after the IL is started.

        This works only if the normal as well as the fast cycle time are defined
        with values > 0.
        """
        return self._get_attribute('GenMsgFastOnStart')

    @gen_msg_fast_on_start.setter
    def gen_msg_fast_on_start(self, value):
        self._set_int_attribute('GenMsgFastOnStart', 0, 2147483647, value)

    @property
    def gen_msg_il_support(self):
        """
        Set to Yes if the message is handled by the interaction layer.
        """
        return bool(self._get_attribute('GenMsgILSupport'))

    @gen_msg_il_support.setter
    def gen_msg_il_support(self, value):
        self._set_yes_no_attribute('GenMsgILSupport', int(value))

    @property
    def tp_j1939_var_dlc(self):
        """
        Set to Yes if the message is handled by the interaction layer.
        """
        return bool(self._get_attribute('TpJ1939VarDlc'))

    @tp_j1939_var_dlc.setter
    def tp_j1939_var_dlc(self, value):
        self._set_yes_no_attribute('TpJ1939VarDlc', int(value))

    @property
    def diag_request(self):
        """
        Specifies that the message is used for a diagnostic request.
        """
        return bool(self._get_attribute('DiagRequest'))

    @diag_request.setter
    def diag_request(self, value):
        self._set_yes_no_attribute('DiagRequest', int(value))

    @property
    def diag_response(self):
        """
        Specifies that the message is used for a diagnostic response.
        """
        return bool(self._get_attribute('DiagResponse'))

    @diag_response.setter
    def diag_response(self, value):
        self._set_yes_no_attribute('DiagResponse', int(value))

    @property
    def nm_message(self):
        """
        Specifies that the message is used as a network management message of a particular node.
        """
        return bool(self._get_attribute('NmMessage'))

    @nm_message.setter
    def nm_message(self, value):
        self._set_yes_no_attribute('NmMessage', int(value))

    @property
    def gen_msg_auto_gen_dsp(self):
        return bool(self._get_attribute('GenMsgAutoGenDsp'))

    @gen_msg_auto_gen_dsp.setter
    def gen_msg_auto_gen_dsp(self, value):
        self._set_yes_no_attribute('GenMsgAutoGenDsp', int(value))

    @property
    def gen_msg_auto_gen_snd(self):
        return bool(self._get_attribute('GenMsgAutoGenSnd'))

    @gen_msg_auto_gen_snd.setter
    def gen_msg_auto_gen_snd(self, value):
        self._set_yes_no_attribute('GenMsgAutoGenSnd', int(value))

    @property
    def gen_msg_alt_setting(self):
        return self._get_attribute('GenMsgAltSetting')

    @gen_msg_alt_setting.setter
    def gen_msg_alt_setting(self, value):
        self._set_str_attribute('GenMsgAltSetting', value)

    @property
    def gen_msg_conditional_send(self):
        return self._get_attribute('GenMsgConditionalSend')

    @gen_msg_conditional_send.setter
    def gen_msg_conditional_send(self, value):
        self._set_str_attribute('GenMsgConditionalSend', value)

    @property
    def gen_msg_ev_name(self):
        return self._get_attribute('GenMsgEVName')

    @gen_msg_ev_name.setter
    def gen_msg_ev_name(self, value):
        self._set_str_attribute('GenMsgEVName', value)

    @property
    def gen_msg_post_if_setting(self):
        return self._get_attribute('GenMsgPostIfSetting')

    @gen_msg_post_if_setting.setter
    def gen_msg_post_if_setting(self, value):
        self._set_str_attribute('GenMsgPostIfSetting', value)

    @property
    def gen_msg_post_setting(self):
        return self._get_attribute('GenMsgPostSetting')

    @gen_msg_post_setting.setter
    def gen_msg_post_setting(self, value):
        self._set_str_attribute('GenMsgPostSetting', value)

    @property
    def gen_msg_pre_if_setting(self):
        return self._get_attribute('GenMsgPreIfSetting')

    @gen_msg_pre_if_setting.setter
    def gen_msg_pre_if_setting(self, value):
        self._set_str_attribute('GenMsgPreIfSetting', value)

    @property
    def gen_msg_pre_setting(self):
        return self._get_attribute('GenMsgPreSetting')

    @gen_msg_pre_setting.setter
    def gen_msg_pre_setting(self, value):
        self._set_str_attribute('GenMsgPreSetting', value)

    @property
    def gen_msg_send_type(self):
        """
        Defines the message related send type.

        This attribute together with the send types of the signals placed on the
        message define the overall transmit behavior of the message.
        """
        if 'GenMsgSendType' in self.dbc.attributes:
            value = self.dbc.attributes['GenMsgSendType'].value
            return self.dbc.attributes['GenMsgSendType'].definition.choices[value]

    @gen_msg_send_type.setter
    def gen_msg_send_type(self, value):
        if 'GenMsgSendType' in self.dbc.attributes:
            self.dbc.attributes['GenMsgSendType'].value = value
        else:
            if 'GenMsgSendType' in self.dbc.attribute_definitions:
                definition = self.dbc.attribute_definitions['GenMsgSendType']
            else:
                definition = attribute_definition.AttributeDefinition(
                    'GenSigSendType',
                    default_value=0,
                    kind='SG_',
                    type_name='ENUM',
                    choices={
                        0: 'cyclic',
                        1: 'spontaneous',
                        2: 'cyclicIfActive',
                        3: 'spontaneousWithDelay',
                        4: 'cyclicAndSpontaneous',
                        5: 'cyclicAndSpontaneousWithDelay',
                        6: 'spontaneousWithRepetition',
                        7: 'cyclicIfActiveAndSpontaneousWD'
                    }
                )

            choices = {v: k for k, v in definition.choices.items()}

            self.dbc.attributes['GenMsgSendType'] = attribute.Attribute(choices[value], definition)

    @property
    def dbc_frame_id(self):
        frame_id = int(self.frame_id)

        if self.is_extended_frame:
            frame_id |= 0x80000000

        return frame_id

    def __str__(self):
        res = [
            'BO_ {frame_id} {name}: {length} {senders}'.format(
                frame_id=int(self.frame_id),
                name=self.name,
                length=self.length,
                senders=self.senders[0].name if self.senders else 'Vector__XXX'
            )
        ]

        res += [
            str(signal) for signal in self.signals[::-1]
        ]

        return '\n'.join(res)

