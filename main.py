# ModbusAsyncWeb. Single script app @Miguel Garcia Duch (27/09/2023)

import streamlit as st
from async_modbus import modbus_for_url
import asyncio
import struct
import numpy as np

def word_list_to_value(words, kind):
    if kind == "int32":
        k = 'i'
    elif kind == "float32":
        k = 'f'
    elif kind == "uint32":
        k = "I"
    elif kind == "uint32_satec":
        k = "I"
    else:
        raise ValueError('Invalid kind. Expected "int32", "uint32", "float32", or "uint32_satec".')
    # For the uint32_satec kind, you can process the words differently
    # but still use the unpacking mechanism.
    if kind == "uint32_satec":
        processed_words = [
            int(np.uint16(word1)) + int(np.uint16(word2)) * 2**16
            for word1, word2 in zip(words[::2], words[1::2])
        ]
        return [struct.unpack('!' + k, struct.pack('!I', word))[0] for word in processed_words]
    return [
        struct.unpack('!'+  k, struct.pack('!HH', *word_pair))[0] for word_pair in zip(words[::2], words[1::2])
    ]


def convert_reading(register_list, datatype="int16"):
    # Convert a list of register values based on the specified data type.
    # Parameters:
    #   - register_list: List of register values.
    #   - num_registers: Number of registers.
    #   - datatype: One of "float", "int32", "int16", "uint16", "uint32", or "uint32_alt".
    # Returns:
    #   - List of converted register values.

    readings = []
    if datatype == "float":
        readings = word_list_to_value(register_list, "float32")
    elif datatype == "int32":
        readings = word_list_to_value(register_list, "int32")
    elif datatype == "uint32":
        readings = word_list_to_value(register_list, "uint32")
    elif datatype == "uint32_alt":
        readings = word_list_to_value(register_list, "uint32_alt")
    elif datatype == "int16":
        readings = [int(np.int16(v)) for v in register_list]
    elif datatype == "uint16":
        readings = [int(np.uint16(v)) for v in register_list]
    return readings


async def read_modbus_data(host, port, address, register_length=1, data_type="int16"):
    # Asynchronously read data from Modbus server and display it in Streamlit.
    # Parameters:
    #   - host: Modbus server IP address.
    #   - port: Modbus server port.
    #   - address: Starting address for reading.
    #   - register_length: Number of registers to read.
    #   - data_type: One of "float", "int32", "int16",  or "uint" equivalents.

    client = modbus_for_url(f"tcp://{host}:{port}")
    try:
        result = await client.read_holding_registers(
            slave_id=0x01, starting_address=address, quantity=register_length
        )
        converted_result = convert_reading(result, data_type)
        return converted_result
    except Exception as e:
        st.write("Error: ", e)


async def read_multiple_modbus_data(
    # Asynchronously manage concurrent calls
    host, port, address, register_length, data_type, attempts
):
    results = []
    for _ in range(attempts):
        result = await read_modbus_data(host, port, address, register_length, data_type)
        results += result
    return results


def main():
    # Main function to render the Streamlit interface and handle user interactions.

    st.title(":satellite_antenna: Async Modbus Reader :satellite_antenna:")
    cols1, cols2, cols3 = st.columns([1, 1, 1])
    with cols1:
        host = st.text_input("Modbus host IP", "45.95.197.176")
        port = st.text_input("Port", 48418)
        address = st.text_input("Address", 14720)
    with cols3:
        data_type = st.selectbox(
            "Data Type", ["int16", "uint16", "int32", "uint32", "uint32_alt", "float"]
        )
        register_length = st.selectbox("Length", [1, 2, 4, 8, 16])
        attempts = st.selectbox("nº attempts:", [1, 3, 5])
    with cols2:
        if st.button("Submit"):
            results = asyncio.run(
                read_multiple_modbus_data(
                    host=host,
                    port=int(port),
                    address=int(address),
                    register_length=int(register_length),
                    data_type=data_type,
                    attempts=int(attempts),
                )
            )
            st.write("Response: ", results)


if __name__ == "__main__":
    main()
