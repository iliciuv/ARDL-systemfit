# Async-Modubus Streamlit WebApp
Minimal implementation of an asyncronous modbus web-client for getting readings from TCP devices.

It has been built using streamlit which allows a really easy implementation of a user interface for asyncmodbus in a single file app of around 100 lines of code.

## Modificable Parameters:
    - host: Modbus server IP address.
    - port: Modbus server port.
    - address: Starting address for reading.
    - register_length: Number of registers to read.
    - data_type: Data type for conversion. One of "float", "int32", "int16", or "uint16".

## Live example in share.streamlit.io:

-----------------------------------
https://webmodbusclient.streamlit.app/
-----------------------------------
