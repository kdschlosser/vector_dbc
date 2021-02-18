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

from distutils.core import setup

LONG_DESCRIPTION = '''\
Vector CANdb++ DBC file parser

This is a modified version of the dbc file parser that is included with cantools written by Erik Moqvist

https://github.com/eerimoq/cantools

Changes made:
Removed everything except for the pieces needed to read and write DBC files.
Improved the overall performance of the code
Added 103 Vector defined attributes
Added handling of GMParameterId's 
Added proper decoding of GMParameterId's and J1939 PDU Id's
Added support for ECU's
Fixed default attributes not propigating to the respective ovject types
Added classes that represent a couple of different types of frame id's
Added listing RX and TX signals that are attached to a node
Added receivers list to messages
Added encoding and decoding using a node
Added encoding via a signal
'''

setup(
    name='vector_dbc',
    version='0.1.0b',
    author='Kevin Schlosser',
    maintainer='Kevin Schlosser',
    url='https://github.com/kdschlosser/vector_dbc',
    license='MIT',
    description='Vector CANdb++ DBC file parser',
    long_description=LONG_DESCRIPTION,
    keywords=['can', 'can bus', 'dbc', 'kcd', 'automotive', 'vector', 'CANdb', 'CANdb++'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    requires=['textparser', 'bitstruct'],
)
