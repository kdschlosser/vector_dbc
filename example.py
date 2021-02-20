import vector_dbc

db = vector_dbc.Database.load('OBDII.dbc')

print('=== Database Metadata ===')
print()
print('version_year:', db.version_year)
print('version_day:', db.version_day)
print('version_week:', db.version_week)
print('version:', db.version)
print('version_number:', db.version_number)
print('db_name:', db.db_name)
print('bus_type:', db.bus_type)
print('protocol_type:', db.protocol_type)
print('manufacturer:', db.manufacturer)
print()
print('=== End Database Metadata ===')
print()
print('=== OBDII Encoded Requests ===')
print()
for signal in db.get_message('TX').signals:

    if signal.name in ('length_tx', 'mode', 'pid'):
        continue

    data = signal.encode()
    print(signal.name + ':', data.frame_id_hex + ',', data.hex)

print()
print('=== End OBDII Encoded Requests ===')
print()
print('=== Simulated Response Frame ===')
print()
rx = db.get_message('RX')
data = dict(
    mode='Live Data',
    response=2,
    length=3,
    VehicleSpeed=200,
    pid='VehicleSpeed'
)

print('encoding a test response:', data)
encoded_data = rx.encode(data)
print('encoded data:', encoded_data.frame_id_hex + ',', encoded_data.hex)

decoded_data = db.decode_message(encoded_data.frame_id, encoded_data)
response = {}
for signal in decoded_data:
    value = signal.value
    response[signal.name] = value
    if signal.name in ('mode', 'response', 'length', 'pid'):
        continue

    print()
    print(signal.name + ':', value, signal.unit)

print()
print('decoded test frame:', response)
print('decoded data same as test data:', data == response)
print()
print('=== End Simulated Response Frame ===')
print()
