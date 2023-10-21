# ModbusAsyncWeb. Single script app @Miguel Garcia Duch (27/09/2023)

import streamlit as st
from async_modbus import modbus_for_url
import asyncio
import struct
import numpy as np
from typing import List, Union


# Function to convert a list of words based on the specific conversion type 'k'
def word_list_to_value(words: List[int], k: str) -> List[Union[int, float]]:
    # Special handling for "uint32_alt"
    if k == "uint32_alt":
        processed_words = [
            int(np.uint16(word1)) + int(np.uint16(word2)) * 2**16
            for word1, word2 in zip(words[::2], words[1::2])
        ]
        return [struct.unpack('!' + 'I', struct.pack('!I', word))[0] for word in processed_words]

    # Standard handling for other types
    return [struct.unpack('!'+  k, struct.pack('!HH', *word_pair))[0] for word_pair in zip(words[::2], words[1::2])]


# Function to convert a list of register values based on the specified data type
def convert_reading(register_list: List[int], datatype: str = "int16") -> List[Union[int, float]]:
    if datatype == "int16":
        return [int(np.int16(v)) for v in register_list]
    elif datatype == "uint16":
        return [int(np.uint16(v)) for v in register_list]

    # Dictionary to map data types to their respective conversion types
    type_map = {
        "float": 'f',
        "int32": 'i',
        "uint32": 'I',
        "uint32_alt": 'uint32_alt'  # Use a unique identifier for the special case
    }

    # Check if the given data type exists in the type_map
    if datatype in type_map:
        return word_list_to_value(register_list, type_map[datatype])
    else:
        raise ValueError(f"Invalid datatype. Expected one of {list(type_map.keys())}, got {datatype}")


# Asynchronously read data from Modbus server and display it in Streamlit.
async def read_modbus_data(host, port, address, register_length=1, data_type="int16"):
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
        return []  # Ensure we always return a list


# Asynchronously manage concurrent calls
async def read_multiple_modbus_data(
    host, port, address, register_length, data_type, attempts
):
    results = []
    for _ in range(attempts):
        result = await read_modbus_data(host, port, address, register_length, data_type)
        results += result
    return results


def main():
    # Main function to render the Streamlit interface and handle user interactions.

    st.title(":satellite_antenna: Asynchronous Modbus Reader :satellite_antenna:")
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
        st.divider()
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
        st.divider()

if __name__ == "__main__":
    main()
