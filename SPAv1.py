# ModbusAsyncApp.py
import streamlit as st
from async_modbus import modbus_for_url
import asyncio
import struct
import numpy as np

def word_list_to_value(words, kind):
    # Convert a list of words (16-bit values) to their respective int32 or float32 representations.
    # Parameters:
    #   - words: List of 16-bit values.
    #   - kind: Data type for conversion. Either "int32" or "float32".
    # Returns:
    #   - List of converted values.

    if kind == "int32":
        k = "i"
    elif kind == "float32":
        k = "f"
    else:
        raise ValueError('Invalid kind. Expected "int32" or "float32".')
    return [
        struct.unpack("!" + k, struct.pack("!HH", *word_pair))[0]
        for word_pair in zip(words[::2], words[1::2])
    ]

def convert_reading(register_list, datatype="int16"):
    # Convert a list of register values based on the specified data type.
    # Parameters:
    #   - register_list: List of register values.
    #   - num_registers: Number of registers.
    #   - datatype: Data type for conversion. One of "float", "int32", "int16", "uint16", or "int16_alt".
    # Returns:
    #   - List of converted register values.

    readings = []
    if datatype == "float":
        readings = word_list_to_value(register_list, "float32")
    elif datatype == "int32":
        readings = word_list_to_value(register_list, "int32")
    elif datatype == "int16":
        readings = [int(np.int16(v)) for v in register_list]
    elif datatype == "uint16":
        readings = [int(np.uint16(v)) for v in register_list]
    elif datatype == "int16_alt":
        readings = [int(v) for v in register_list]
    return readings

async def read_modbus_data(host, port, address, register_length=1, data_type="int16"):
    # Asynchronously read data from Modbus server and display it in Streamlit.
    # Parameters:
    #   - host: Modbus server IP address.
    #   - port: Modbus server port.
    #   - address: Starting address for reading.
    #   - register_length: Number of registers to read.
    #   - data_type: Data type for conversion. One of "float", "int32", "int16", or "uint16".

    client = modbus_for_url(f"tcp://{host}:{port}")
    try:
        result = await client.read_holding_registers(slave_id=0x01, starting_address=address, quantity=register_length)
        converted_result = convert_reading(result, data_type)
        return converted_result
    except Exception as e:
        st.write("Error: ", e)

async def read_multiple_modbus_data(host, port, address, register_length, data_type, attempts):
    results = []
    for _ in range(attempts):
        result = await read_modbus_data(host, port, address, register_length, data_type)
        results += result
    return results

def main():
    # Main function to render the Streamlit interface and handle user interactions.
    st.title("Async Modbus Reader")
    cols1, cols2, cols3 = st.columns([1, 1, 1])
    with cols1:
        host = st.text_input("Modbus host IP", "45.95.197.176")
        port = st.text_input("Port", "48418")
        address = st.text_input("Address", "14720")
    with cols2:
        register_length = st.text_input("Length", "1")
        data_type = st.selectbox("Data Type", ["int16", "uint16", "int16_alt", "int32", "float"])
        attempts = st.selectbox("nº attempts:", [1, 5, 10])
    with cols3:
        if st.button("Submit"):
            results = asyncio.run(read_multiple_modbus_data(
                host,
                int(port),
                int(address),
                int(register_length),
                data_type,
                int(attempts)))

            st.write("Response: ", results)

if __name__ == "__main__":
    main()
