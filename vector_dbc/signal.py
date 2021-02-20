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

from .errors import EncodeError
from .comment import SignalComment
from . import sg_mul_val


class Decimal(object):
    """
    Holds the same values as
    :attr:`~cantools.database.can.Signal.scale`,
    :attr:`~cantools.database.can.Signal.offset`,
    :attr:`~cantools.database.can.Signal.minimum` and
    :attr:`~cantools.database.can.Signal.maximum`, but as
    ``decimal.Decimal`` instead of ``int`` and ``float`` for higher
    precision (no rounding errors).
    """

    def __init__(self, scale=None, offset=None, minimum=None, maximum=None):
        self._scale = scale
        self._offset = offset
        self._minimum = minimum
        self._maximum = maximum

    @property
    def scale(self):
        """The scale factor of the signal value as ``decimal.Decimal``."""
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value

    @property
    def offset(self):
        """The offset of the signal value as ``decimal.Decimal``."""
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value

    @property
    def minimum(self):
        """The minimum value of the signal as ``decimal.Decimal``, or ``None`` if unavailable."""
        return self._minimum

    @minimum.setter
    def minimum(self, value):
        self._minimum = value

    @property
    def maximum(self):
        """The maximum value of the signal as ``decimal.Decimal``, or ``None`` if unavailable."""
        return self._maximum

    @maximum.setter
    def maximum(self, value):
        self._maximum = value


class Signal(attribute.AttributeMixin):
    """
    A CAN signal with position, size, unit and other information. A
    signal is part of a message.

    Signal bit numbering in a message:

    .. code:: text

       Byte:       0        1        2        3        4        5        6        7
              +--------+--------+--------+--------+--------+--------+--------+--------+--- - -
              |        |        |        |        |        |        |        |        |
              +--------+--------+--------+--------+--------+--------+--------+--------+--- - -
       Bit:    7      0 15     8 23    16 31    24 39    32 47    40 55    48 63    56

    Big endian signal with start bit 2 and length 5 (0=LSB, 4=MSB):

    .. code:: text

       Byte:       0        1        2        3
              +--------+--------+--------+--- - -
              |    |432|10|     |        |
              +--------+--------+--------+--- - -
       Bit:    7      0 15     8 23    16 31

    Little endian signal with start bit 2 and length 9 (0=LSB, 8=MSB):

    .. code:: text

       Byte:       0        1        2        3
              +--------+--------+--------+--- - -
              |543210| |    |876|        |
              +--------+--------+--------+--- - -
       Bit:    7      0 15     8 23    16 31
    """
    _marker = 'SG_'

    def __init__(
        self, parent, name, start, length, byte_order='little_endian', is_signed=False,
        scale=1, offset=0, minimum=None, maximum=None, unit=None, choices=None, dbc_specifics=None,
        comment=None, receivers=None, is_multiplexer=False,
        multiplexer_ids=None, multiplexer_signal=None, is_float=False, decimal=None
    ):
        self._name = name
        self._start = start
        self._length = length
        self._byte_order = byte_order
        self._is_signed = is_signed
        self._scale = scale
        self._offset = offset
        self._minimum = minimum
        self._maximum = maximum
        self._decimal = Decimal() if decimal is None else decimal
        self._unit = unit
        self._choices = choices
        self._dbc = dbc_specifics
        self._value = None

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

        if not multiplexer_ids:
            multiplexer_ids = []

        self._receivers = [] if receivers is None else receivers
        self._is_multiplexer = is_multiplexer
        self._is_float = is_float
        self._parent = parent
        self._multiplexer = sg_mul_val.SG_MUL_VAL(self, multiplexer_signal, multiplexer_ids)

    @property
    def message(self):
        return self._parent

    @property
    def name(self):
        """The signal name as a string."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def start(self):
        """The start bit position of the signal within its message."""
        return self._start

    @start.setter
    def start(self, value):
        self._start = value

    @property
    def length(self):
        """The length of the signal in bits."""
        return self._length

    @length.setter
    def length(self, value):
        self._length = value

    @property
    def byte_order(self):
        """Signal byte order as ``'little_endian'`` or ``'big_endian'``."""
        return self._byte_order

    @byte_order.setter
    def byte_order(self, value):
        self._byte_order = value

    @property
    def is_signed(self):
        """
        ``True`` if the signal is signed, ``False`` otherwise. Ignore this
        attribute if :data:`~cantools.db.Signal.is_float` is ``True``.
        """
        if self.is_float:
            return None

        return self._is_signed

    @is_signed.setter
    def is_signed(self, value):
        if self.is_float:
            raise ValueError('This cannot be set when the signal data type is set to float')
        self._is_signed = value

    @property
    def is_float(self):
        """``True`` if the signal is a float, ``False`` otherwise."""
        return self._is_float

    @is_float.setter
    def is_float(self, value):
        self._is_float = value

    @property
    def scale(self):
        """The scale factor of the signal value."""
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value

    @property
    def offset(self):
        """The offset of the signal value."""
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value

    @property
    def minimum(self):
        """The minimum value of the signal, or ``None`` if unavailable."""
        return self._minimum

    @minimum.setter
    def minimum(self, value):
        self._minimum = value

    @property
    def maximum(self):
        """The maximum value of the signal, or ``None`` if unavailable."""
        return self._maximum

    @maximum.setter
    def maximum(self, value):
        self._maximum = value

    @property
    def decimal(self):
        """
        The high precision values of
        :attr:`~cantools.database.can.Signal.scale`,
        :attr:`~cantools.database.can.Signal.offset`,
        :attr:`~cantools.database.can.Signal.minimum` and
        :attr:`~cantools.database.can.Signal.maximum`.

        See :class:`~cantools.database.can.signal.Decimal` for more
        details.
        """
        return self._decimal

    @property
    def unit(self):
        """The unit of the signal as a string, or ``None`` if unavailable."""
        return self._unit

    @unit.setter
    def unit(self, value):
        self._unit = value

    @property
    def choices(self):
        """A dictionary mapping signal values to enumerated choices, or ``None`` if unavailable."""
        return self._choices

    @property
    def dbc(self):
        """An object containing dbc specific properties like e.g. attributes."""
        return self._dbc

    @dbc.setter
    def dbc(self, value):
        self._dbc = value

    @property
    def is_updated(self):
        return self._value is not None

    @property
    def value(self):
        val = self._value
        self._value = None
        return val

    @property
    def comments(self):
        """The dictionary with the descriptions of the signal in multiple languages. ``None`` if unavailable."""

        for key, val in list(self._comments.items())[:]:
            if val is not None:
                if isinstance(val, bytes):
                    val = val.decode('utf-8')
                if not isinstance(val, SignalComment):
                    val = SignalComment(val)
                    val.signal = self

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
                if not isinstance(val, (str, SignalComment)):
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

                if not isinstance(comment, SignalComment):
                    comment = SignalComment(comment)
                    comment.signal = self
                    self._comments['EN'] = comment

        else:
            if isinstance(comment, bytes):
                comment = comment.decode('utf-8')

            if not isinstance(comment, SignalComment):
                comment = SignalComment(comment)
                comment.signal = self
                self._comments[None] = comment

        return comment

    @comment.setter
    def comment(self, value):
        if isinstance(value, bytes):
            value = value.decode('utf-8')

        if value is not None and not isinstance(value, (str, SignalComment)):
            value = str(value)

        self._comments = {None: value}

    @property
    def receivers(self):
        """A list of all receiver nodes of this signal."""
        receivers = [node for node in self.message.database.nodes if node.name in self._receivers]
        return receivers

    @property
    def is_multiplexer(self):
        """``True`` if this is the multiplexer signal in a message, ``False` otherwise."""
        return self._is_multiplexer

    @is_multiplexer.setter
    def is_multiplexer(self, value):
        self._is_multiplexer = value

    @property
    def multiplexer(self):
        """The multiplexer ids list if the signal is part of a multiplexed message, ``None`` otherwise."""
        return self._multiplexer

    def choice_string_to_number(self, string):
        for choice_number, choice_string in self.choices.items():
            if choice_string == string:
                return choice_number

    def encode(self, data=None, scaling=True, padding=False, strict=True):
        """
        Encode a signal directly

        This will encode a message where all other signals in the message have initial
        values set and you want to ue those initial values. If there is a multiplexer_signal
        for this signal then that will also get set to this signal name

        :param data: the data to set or None if there has been an initial value set and that is what is to be used
        :type data: optional, any
        """

        if self._parent is None:
            raise EncodeError('This signal is not attached to any database or message')
        if data is None:
            if self.gen_sig_start_value is not None:
                data = {self.name: self.gen_sig_start_value + self.offset}
            else:
                raise EncodeError(
                    "You must supply a signal value for signal {0}".format(self.name)
                )
        else:
            data = {self.name: data}

        if self.multiplexer.is_ok:
            m_signal = self.multiplexer.multiplexer_signal
            data[m_signal.name] = m_signal.choices[self.multiplexer[0]]

        return self._parent.encode(data, scaling=scaling, padding=padding, strict=strict)

    @property
    def gen_sig_send_type(self):
        """
        Defines the signal related send type.

        This attribute together with the message related send type and the
        send types of the other signals placed on the message define the overall
        transmit behavior of the message.
        """
        value = self._get_attribute('GenSigSendType')
        if value is not None:
            return self.dbc.attributes['GenSigSendType'].definition.choices[value]

    @gen_sig_send_type.setter
    def gen_sig_send_type(self, value):
        if 'GenSigSendType' in self.dbc.attributes:
            self.dbc.attributes['GenSigSendType'].value = value
        else:
            if 'GenSigSendType' in self.dbc.attribute_definitions:
                definition = self.dbc.attribute_definitions['GenSigSendType']
            else:
                definition = attribute_definition.AttributeDefinition(
                    'GenSigSendType',
                    default_value=0,
                    kind='SG_',
                    type_name='ENUM',
                    choices={
                        0: 'Cyclic',
                        1: 'OnWrite',
                        2: 'OnWriteWithRepetition',
                        3: 'OnChange',
                        4: 'OnChangeWithRepetition',
                        5: 'IfActive',
                        6: 'IfActiveWithRepetition',
                        7: 'NoSigSendType'
                    }
                )

            choices = {v: k for k, v in definition.choices.items()}

            self.dbc.attributes['GenSigSendType'] = attribute.Attribute(choices[value], definition)

    @property
    def gen_sig_inactive_value(self):
        """
        Defines the inactive value of a signal.

        This value is only used for signal send type IfActive. If the signal
        value is unequal to GenSigInactiveValue the message the signal is placed
        on will be transmitted periodically with a periodicity of GenMsgCycleTimeFast.
        The signals inactive value is given as a signals raw value in this attribute.
        """
        return self._get_attribute('GenSigInactiveValue')

    @gen_sig_inactive_value.setter
    def gen_sig_inactive_value(self, value):
        self._set_int_attribute('GenSigInactiveValue', 0, 2147483647, value)

    @property
    def gen_sig_start_value(self):
        """
        Defines the start or initial value of the signal.

        This value is send after system start-up until the application
        sets the signal value the first time. The signals start value is
        given as a signals raw value in this attribute.
        """
        return self._get_attribute('GenSigStartValue')

    @gen_sig_start_value.setter
    def gen_sig_start_value(self, value):
        self._set_int_attribute('GenSigStartValue', 0, 2147483647, value)

    @property
    def gen_sig_timeout_time(self):
        """
        Defines the time of the signal receive timeout.

        If the message of the signal isn't received for this time interval a
        receive timeout will occur. The action performed after the timeout
        depends on the interaction layer used. The suffix <_ECU> gives the
        name of the receiving ECU if the attribute is defined for signals
        instead of Node-mapped Tx-Signal relations.
        """
        return self._get_attribute('GenSigTimeoutTime')

    @gen_sig_timeout_time.setter
    def gen_sig_timeout_time(self, value):
        self._set_int_attribute('GenSigTimeoutTime', 0, 2147483647, value)

    @property
    def gen_sig_timeout_msg(self):
        """
        Defines the ID of the message the signal is supervised by.

        If the message with the given ID is received by the receiver node, no
        signal timeout will occur. The timeout itself is defined in attribute
        GenSigTimeout-Time<_ECU>. The suffix <_ECU> gives the name of the
        receiving ECU if the attribute is defined for signals instead of
        Node-mapped Tx-Signal relations.
        """
        return self._get_attribute('GenSigTimeoutMsg')

    @gen_sig_timeout_msg.setter
    def gen_sig_timeout_msg(self, value):
        self._set_hex_attribute('GenSigTimeoutMsg', 0x0, 0x7FF, value)

    @property
    def nwm_wakeup_allowed(self):
        """
        This attribute is set to No for signals that have no effect on the NM.
        """
        return bool(self._get_attribute('NWM-WakeupAllowed'))

    @nwm_wakeup_allowed.setter
    def nwm_wakeup_allowed(self, value):
        self._set_yes_no_attribute('NWM-WakeupAllowed', value)

    @property
    def sig_type(self):
        """
        The valid value range and the interpretation of the signal
        value is specified with the attribute SigType.

        By using SigType it is possible to display only valid signal values in the Graphics Window.
        If the attribute is not defined the entire value range is valid.

        Valid Values:
            Default: normal signal, no protocol-specific interpretation
            Range: Signals with the attribute value Range are interpreted according to SAE J1939-71.
                   The available value range is restricted due to coding additional information. The
                   attribute value can only be used for signals of value type Unsigned.

                                       1 Byte    2 Byte         4 Byte
                valid signal           0..FAh    0..FAFFh       0..FAFFFFFFh
                parameter specific     FBh       FB00h..FBFFh   FB000000h..FBFFFFFFh
                reserved               FCh..FDh  FC00h..FDFFh   FC000000h..FDFFFFFFh
                error                  FEh       FE00h..FEFFh   FE000000h..FEFFFFFFh
                not available          FFh       FF00h..FFFFh   FF000000h..FFFFFFFFh


            RangeSigned: Signals with the attribute value RangeSigned are interpreted according to
                         NMEA2000® appendix B4. The available value range is restricted due to coding additional
                         information. The attribute value can only be used for signals of value type Signed.

                                       1 Byte            2 Byte                  4 Byte
                valid signal           0..7Ch, 80h..FFh  0..7FFCh, 8000h..FFFFh  0..7FFFFFFCh, 80000000h..FFFFFFFFh
                parameter specific     7Dh               7FFDh                   7FFFFFFDh
                error                  7Eh               7FFEh                   7FFFFFFEh
                not available          7Fh               7FFFh                   7FFFFFFFh



            ASCII: A signal of this type contains a string of fix length.
                   The length of the string is defined by the size of the signal.

                                       1 Byte
                valid signal           01h..FEh
                error                  00h
                not available          FFh


            Discrete:

                                       2 Bit
                not active             0
                active                 1
                error                  2
                not available          3

            Control:

                                       2 Bit
                deactivate             0
                activate               1
                reserved               2
                do not change          3



            ReferencePGN: The signal contains a PGN, i.E. the RQST (PGN EA00h) Parameter Group contains
                a signal with the requested PGN. The Trace Window and Data Window shows the name of the
                Parameter Group from the database.
            DTC: The signal contains a diagnostic trouble code (32 bit, inclusive SPN, FMI and OC). The
                Trace Window and Data Window show the name of the signal depending on the SPN. The
                Conversion Method Version 4 or Version 1, depending on the Conversion Method Bit, is used.
            StringDelimiter: String of variable length which ends with a delimiter ("*" or "2Ah"). The length
                of the signal in the database must be set to 8 bit (minimum length of a string signal).
            StringLength: String of variable length which contains the number of characters in the first or
                first two bytes (Intel format). The signal size in the database must be set to 8 bit for 1
                byte length or 16 bit for 2 byte length (minimum length of a string signal).
            StringLengthCtrl: String of variable length which contains the signal length in bytes (including
                the size and control bytes) in the first or first two bytes (Intel format) and a control byte
                (0=Unicode (UTF16), 1=ASCII) after the length. The signal size in the database must be set to
                16 bit for 1 byte length or 24 bit for 2 byte length (minimum length of a string signal).
            MessageCounter:
            MessageChecksum:
        """
        if 'SigType' in self.dbc.attributes:
            value = self.dbc.attributes['SigType'].value
            return self.dbc.attributes['SigType'].definition.choices[value]

    @sig_type.setter
    def sig_type(self, value):
        if 'SigType' in self.dbc.attributes:
            self.dbc.attributes['SigType'].value = value
        else:

            if 'SigType' in self.dbc.attribute_definitions:
                definition = self.dbc.attribute_definitions['SigType']
            else:

                definition = attribute_definition.AttributeDefinition(
                    'SigType',
                    default_value=0,
                    kind='SG_',
                    type_name='ENUM',
                    choices={
                        0: 'Default',
                        1: 'Range',
                        2: 'RangeSigned',
                        3: 'ASCII',
                        4: 'Discrete',
                        5: 'Control',
                        6: 'ReferencePGN',
                        7: 'DTC',
                        8: 'StringDelimiter',
                        9: 'StringLength',
                        10: 'StringLengthCtrl',
                        11: 'MessageCounter',
                        12: 'MessageChecksum'
                    }
                )

            choices = {v: k for k, v in definition.choices.items()}

            self.dbc.attributes['SigType'] = attribute.Attribute(choices[value], definition)

    @property
    def spn(self):
        """
        With the attribute SPN, the Suspect Parameter Number is defined

        The SPN is specified in the J1939 specification. This attribute is used,
        for example, by the J1939 DTC Monitor.
        """
        return self._get_attribute('SPN')

    @spn.setter
    def spn(self, value):
        self._set_int_attribute('SPN', 0, 524287, value)

    @property
    def gen_sig_alt_setting(self):
        return self._get_attribute('GenSigAltSetting')

    @gen_sig_alt_setting.setter
    def gen_sig_alt_setting(self, value):
        self._set_str_attribute('GenSigAltSetting', value)

    @property
    def gen_sig_assign_setting(self):
        return self._get_attribute('GenSigAssignSetting')

    @gen_sig_assign_setting.setter
    def gen_sig_assign_setting(self, value):
        self._set_str_attribute('GenSigAssignSetting', value)

    @property
    def gen_sig_conditional_send(self):
        return self._get_attribute('GenSigConditionalSend')

    @gen_sig_conditional_send.setter
    def gen_sig_conditional_send(self, value):
        self._set_str_attribute('GenSigConditionalSend', value)

    @property
    def gen_sig_ev_name(self):
        return self._get_attribute('GenSigEVName')

    @gen_sig_ev_name.setter
    def gen_sig_ev_name(self, value):
        self._set_str_attribute('GenSigEVName', value)

    @property
    def gen_sig_post_if_setting(self):
        return self._get_attribute('GenSigPostIfSetting')

    @gen_sig_post_if_setting.setter
    def gen_sig_post_if_setting(self, value):
        self._set_str_attribute('GenSigPostIfSetting', value)

    @property
    def gen_sig_post_setting(self):
        return self._get_attribute('GenSigPostSetting')

    @gen_sig_post_setting.setter
    def gen_sig_post_setting(self, value):
        self._set_str_attribute('GenSigPostSetting', value)

    @property
    def gen_sig_pre_if_setting(self):
        return self._get_attribute('GenSigPreIfSetting')

    @gen_sig_pre_if_setting.setter
    def gen_sig_pre_if_setting(self, value):
        self._set_str_attribute('GenSigPreIfSetting', value)

    @property
    def gen_sig_pre_setting(self):
        return self._get_attribute('GenSigPreSetting')

    @gen_sig_pre_setting.setter
    def gen_sig_pre_setting(self, value):
        self._set_str_attribute('GenSigPreSetting', value)

    @property
    def gen_sig_receive_setting(self):
        return self._get_attribute('GenSigReceiveSetting')

    @gen_sig_receive_setting.setter
    def gen_sig_receive_setting(self, value):
        self._set_str_attribute('GenSigReceiveSetting', value)

    @property
    def gen_sig_auto_gen_dsp(self):
        return bool(self._get_attribute('GenSigAutoGenDsp'))

    @gen_sig_auto_gen_dsp.setter
    def gen_sig_auto_gen_dsp(self, value):
        self._set_yes_no_attribute('GenSigAutoGenDsp', value)

    @property
    def gen_sig_auto_gen_snd(self):
        return bool(self._get_attribute('GenSigAutoGenSnd'))

    @gen_sig_auto_gen_snd.setter
    def gen_sig_auto_gen_snd(self, value):
        self._set_yes_no_attribute('GenSigAutoGenSnd', value)

    @property
    def gen_sig_env_var_type(self):
        if 'GenSigEnvVarType' in self.dbc.attributes:
            value = self.dbc.attributes['GenSigEnvVarType'].value
            return self.dbc.attributes['GenSigEnvVarType'].definition.choices[value]

    @gen_sig_env_var_type.setter
    def gen_sig_env_var_type(self, value):
        if 'GenSigEnvVarType' in self.dbc.attributes:
            self.dbc.attributes['GenSigEnvVarType'].value = value
        else:

            if 'GenSigEnvVarType' in self.dbc.attribute_definitions:
                definition = self.dbc.attribute_definitions['GenSigEnvVarType']
            else:

                definition = attribute_definition.AttributeDefinition(
                    'GenSigEnvVarType',
                    default_value=2,
                    kind='SG_',
                    type_name='ENUM',
                    choices={
                        0: 'int',
                        1: 'float',
                        2: 'undef'
                    }
                )

            choices = {v: k for k, v in definition.choices.items()}

            self.dbc.attributes['GenSigEnvVarType'] = attribute.Attribute(choices[value], definition)

    def __str__(self):
        if self.is_multiplexer:
            mux = ' M'
        elif self.multiplexer.is_ok:
            mux = ' m{}'.format(self.multiplexer[0])
        else:
            mux = ''

        if self.receivers:
            receivers = ' ' + ','.join(node.name for node in self.receivers)
        else:
            receivers = 'Vector__XXX'

        fmt = (
            ' SG_ {name}{mux} : {start}|{length}@{byte_order}{sign}'
            ' ({scale},{offset})'
            ' [{minimum}|{maximum}] "{unit}" {receivers}'
        )

        res = fmt.format(
                name=self.name,
                mux=mux,
                start=self.start,
                length=self.length,
                receivers=receivers,
                byte_order=(0 if self.byte_order == 'big_endian' else 1),
                sign='-' if self.is_signed else '+',
                scale=self.scale,
                offset=self.offset,
                minimum=0 if self.minimum is None else self.minimum,
                maximum=0 if self.maximum is None else self.maximum,
                unit='' if self.unit is None else self.unit
        )
        return res
