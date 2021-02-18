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

from . import attribute_definition


class AttributeMixin(object):
    dbc = None
    _marker = ''

    def _get_attribute(self, attr_name):
        if attr_name in self.dbc.attributes:
            value = self.dbc.attributes[attr_name].value

            return value

    def _set_yes_no_attribute(self, attr_name, value):
        if attr_name in self.dbc.attributes:
            self.dbc.attributes[attr_name].value = value
        else:

            if attr_name in self.dbc.attribute_definitions:
                definition = self.dbc.attribute_definitions[attr_name]
            else:

                definition = attribute_definition.AttributeDefinition(
                    attr_name,
                    default_value=0,
                    kind=self._marker,
                    type_name='ENUM',
                    choices={0: 'No', 1: 'Yes'}
                )
                self.dbc.attribute_definitions[attr_name] = definition

            self.dbc.attributes[attr_name] = Attribute(int(value), definition)

    def _set_hex_attribute(self, attr_name, minimum, maximum, value):
        self._set_attribute(attr_name, minimum, maximum, value, 'HEX')

    def _set_int_attribute(self, attr_name, minimum, maximum, value):
        self._set_attribute(attr_name, minimum, maximum, value, 'INT')

    def _set_str_attribute(self, attr_name, value):
        if attr_name in self.dbc.attributes:
            self.dbc.attributes[attr_name].value = value
        else:
            if attr_name in self.dbc.attribute_definitions:
                definition = self.dbc.attribute_definitions[attr_name]
            else:

                definition = attribute_definition.AttributeDefinition(
                    attr_name,
                    default_value='',
                    kind=self._marker,
                    type_name='STRING',
                )
                self.dbc.attribute_definitions[attr_name] = definition

            self.dbc.attributes[attr_name] = Attribute(value, definition)

    def _set_attribute(self, attr_name, minimum, maximum, value, type_):
        if attr_name in self.dbc.attributes:
            self.dbc.attributes[attr_name].value = value
        else:
            if attr_name in self.dbc.attribute_definitions:
                definition = self.dbc.attribute_definitions[attr_name]
            else:

                definition = attribute_definition.AttributeDefinition(
                    attr_name,
                    default_value=0,
                    kind=self._marker,
                    type_name=type_,
                    minimum=minimum,
                    maximum=maximum
                )
                self.dbc.attribute_definitions[attr_name] = definition

            self.dbc.attributes[attr_name] = Attribute(value, definition)


class Attribute(object):
    """An attribute that can be associated with nodes/messages/signals."""

    def __init__(self, value, definition):
        self._value = value
        self._definition = definition

    @property
    def name(self):
        """The attribute name as a string."""
        return self._definition.name

    @property
    def value(self):
        """The value that this attribute has."""
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def definition(self):
        """The attribute definition."""
        return self._definition
