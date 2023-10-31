# ModbusAsyncWeb. Single script app @Miguel Garcia Duch (27/09/2023)

import streamlit as st
from async_modbus import modbus_for_url
import asyncio
import struct
import numpy as np

def word_list_to_value(words, kind):
    # Decrypt multiword modbus 32bit registers

    if kind == "int32":
        k = 'i'
    elif kind == "float32":
        k = 'f'
    elif kind == "uint32":
        k = "I"
    elif kind == "uint32 (SATEC)":
        k = "I"
    else:
        raise ValueError('Invalid kind. Expected "int32", "uint32", "float32", or "uint32_satec".')

    # manage an example of "special cases" where two consecutive unit16 work as pseudo- uint32
    if kind == "uint32 (SATEC)":
        processed_words = [
            int(np.uint16(word1)) + int(np.uint16(word2)) * 2**16
            for word1, word2 in zip(words[::2], words[1::2])
        ]
        return [struct.unpack('!' + k, struct.pack('!I', word))[0] for word in processed_words]
    # standard decryption using struct.unpack
    return [
        struct.unpack('!'+  k, struct.pack('!HH', *word_pair))[0] for word_pair in zip(words[::2], words[1::2])
    ]


def convert_reading(register_list, datatype="int16"):
    # Convert a list of register values based on the specified data type.
    # Parameters:
    #   - register_list: List of register values.
    #   - num_registers: Number of registers.
    #   - datatype: One of "float", "int32", "int16", "uint16", "uint32", or "uint32 (SATEC)".

    readings = []
    if datatype == "float":
        readings = word_list_to_value(register_list, "float32")
    elif datatype == "int32":
        readings = word_list_to_value(register_list, "int32")
    elif datatype == "uint32":
        readings = word_list_to_value(register_list, "uint32")
    elif datatype == "uint32 (SATEC)":
        readings = word_list_to_value(register_list, "uint32 (SATEC)")
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
        result = await asyncio.wait_for(client.read_holding_registers(
        slave_id=int(f"1x{slave:02}"), starting_address=address, quantity=register_length, timeout=int(user_timeout)
        converted_result = convert_reading(result, data_type)
        return converted_result
    except asyncio.TimeoutError:
        st.write("Error: timeout exceeded")
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

    st.title(":satellite_antenna: Asynchronous Modbus Client :satellite_antenna:")
    cols1, cols2, cols3 = st.columns([1, 1, 1])
    with cols1:
        host = st.text_input("IP del host:", "45.95.197.176")
        port = st.text_input("Puerto:", 48418)
        address = st.text_input("Registro inicial:", 14720)
        slave = st.text_input("Esclavo:", 1)
    with cols3:
        data_type = st.selectbox(
            "Tipo de dato:", ["int16", "uint16", "int32", "uint32", "uint32 (SATEC)", "float"]
        )
        register_length = st.selectbox("Longitud (bytes):", [1, 2, 4, 8, 16])
        attempts = st.selectbox("Nº intentos:", [1, 3, 5])
        user_timeout = st.text_input("Timeout respuesta (s):", 90)
    with cols2:
        st.divider()
        if st.button("Enviar"):
            message_placeholder = st.empty()  # Create a placeholder
            message_placeholder.text('Realizando petición...')
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
            message_placeholder.empty()  # Clear the placeholder
            st.write("Respuesta: ", results)
        st.divider()

if __name__ == "__main__":
    main()

