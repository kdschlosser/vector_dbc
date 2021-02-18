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


class EnvironmentVariable(attribute.AttributeMixin):
    """A CAN environment variable."""

    _marker = 'EV_'

    def __init__(
        self, name, env_type, minimum, maximum, unit, initial_value,
        env_id, access_type, access_node, comment
    ):
        self._name = name
        self._env_type = env_type
        self._minimum = minimum
        self._maximum = maximum
        self._unit = unit
        self._initial_value = initial_value
        self._env_id = env_id
        self._access_type = access_type
        self._access_node = access_node
        self._comment = comment

    @property
    def name(self):
        """The environment variable name as a string."""
        return self._name

    @property
    def env_type(self):
        """The environment variable type value."""
        return self._env_type

    @env_type.setter
    def env_type(self, value):
        self._env_type = value

    @property
    def minimum(self):
        """The minimum value of the environment variable."""
        return self._minimum

    @minimum.setter
    def minimum(self, value):
        self._minimum = value

    @property
    def maximum(self):
        """The maximum value of the environment variable."""
        return self._maximum

    @maximum.setter
    def maximum(self, value):
        self._maximum = value

    @property
    def unit(self):
        """ The units in which the environment variable is expressed as a string."""
        return self._unit

    @unit.setter
    def unit(self, value):
        self._unit = value

    @property
    def initial_value(self):
        """The initial value of the environment variable."""
        return self._initial_value

    @initial_value.setter
    def initial_value(self, value):
        self._initial_value = value

    @property
    def env_id(self):
        """The id value of the environment variable."""
        return self._env_id

    @env_id.setter
    def env_id(self, value):
        self._env_id = value

    @property
    def access_type(self):
        """The environment variable access type as a string."""
        return self._access_type

    @access_type.setter
    def access_type(self, value):
        self._access_type = value

    @property
    def access_node(self):
        """The environment variable access node as a string."""
        return self._access_node

    @access_node.setter
    def access_node(self, value):
        self._access_node = value

    @property
    def comment(self):
        """The environment variable comment, or ``None`` if unavailable."""
        return self._comment

    @comment.setter
    def comment(self, value):
        self._comment = value

    @property
    def gen_env_auto_gen_ctrl(self):
        return bool(self._get_attribute('GenEnvAutoGenCtrl'))

    @gen_env_auto_gen_ctrl.setter
    def gen_env_auto_gen_ctrl(self, value):
        self._set_yes_no_attribute('GenEnvAutoGenCtrl', value)

    @property
    def gen_env_control_type(self):
        if 'GenEnvControlType' in self.dbc.attributes:
            value = self.dbc.attributes['GenEnvControlType'].value
            return self.dbc.attributes['GenEnvControlType'].definition.choices[value]

    @gen_env_control_type.setter
    def gen_env_control_type(self, value):
        if 'GenEnvControlType' in self.dbc.attributes:
            self.dbc.attributes['GenEnvControlType'].value = value
        else:

            if 'GenEnvControlType' in self.dbc.attribute_definitions:
                definition = self.dbc.attribute_definitions['GenEnvControlType']
            else:

                definition = attribute_definition.AttributeDefinition(
                    'GenEnvControlType',
                    default_value=0,
                    kind='EV_',
                    type_name='ENUM',
                    choices={
                        0: 'NoControl',
                        1: 'SliderHoriz',
                        2: 'SliderVert',
                        3: 'PushButton',
                        4: 'Edit',
                        5: 'BitmapSwitch'
                    }
                )

            choices = {v: k for k, v in definition.choices.items()}

            self.dbc.attributes['GenEnvControlType'] = attribute.Attribute(choices[value], definition)

    @property
    def gen_env_msg_name(self):
        return self._get_attribute('GenEnvMsgName')

    @gen_env_msg_name.setter
    def gen_env_msg_name(self, value):
        self._set_str_attribute('GenEnvMsgName', value)

    @property
    def gen_env_msg_offset(self):
        return self._get_attribute('GenEnvMsgOffset')

    @gen_env_msg_offset.setter
    def gen_env_msg_offset(self, value):
        self._set_int_attribute('GenEnvMsgOffset', 0, 2147483647, value)

    @property
    def gen_env_var_ending_dsp(self):
        return self._get_attribute('GenEnvVarEndingDsp')

    @gen_env_var_ending_dsp.setter
    def gen_env_var_ending_dsp(self, value):
        self._set_str_attribute('GenEnvVarEndingDsp', value)

    @property
    def gen_env_var_ending_snd(self):
        return self._get_attribute('GenEnvVarEndingSnd')

    @gen_env_var_ending_snd.setter
    def gen_env_var_ending_snd(self, value):
        self._set_str_attribute('GenEnvVarEndingSnd', value)

    @property
    def gen_env_var_prefix(self):
        return self._get_attribute('GenEnvVarPrefix')

    @gen_env_var_prefix.setter
    def gen_env_var_prefix(self, value):
        self._set_int_attribute('GenEnvVarPrefix', 0, 2147483647, value)

    @property
    def gen_env_is_generated_dsp(self):
        return bool(self._get_attribute('GenEnvIsGeneratedDsp'))

    @gen_env_is_generated_dsp.setter
    def gen_env_is_generated_dsp(self, value):
        self._set_yes_no_attribute('GenEnvIsGeneratedDsp', value)

    @property
    def gen_env_is_generated_snd(self):
        return bool(self._get_attribute('GenEnvIsGeneratedSnd'))

    @gen_env_is_generated_snd.setter
    def gen_env_is_generated_snd(self, value):
        self._set_yes_no_attribute('GenEnvIsGeneratedSnd', value)
