# Vector CANdb++ DBC file parser

This is a modified version of the dbc file parser that is included with cantools written by Erik Moqvist
https://github.com/eerimoq/cantools

Changes made:

* Removed everything except for the pieces needed to read and write DBC files.
* Improved the overall performance of the code
* Added 103 Vector defined attributes
* Added handling of GMParameterId's 
* Added proper decoding of GMParameterId's and J1939 PDU Id's
* Added support for ECU's
* Fixed default attributes not propigating to the respective ovject types
* Added classes that represent a couple of different types of frame id's
* Added listing RX and TX signals that are attached to a node
* Added receivers list to messages
* Added encoding and decoding using a node
* Added encoding via a signal

This is not a drop in replacement for the cantools dbc parser, 
there are code changes that would need to be made in order for this to run
