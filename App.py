import openai
import streamlit as st

# Leer la API Key y el assistant_id desde secrets
openai_api_key = st.secrets["openai_api_key"]
assistant_id = st.secrets["assistant_id"]

# Crear un cliente de OpenAI
client = openai.Client(api_key=openai_api_key)

# Recuperar el asistente que quieres usar
try:
    assistant = client.beta.assistants.retrieve(assistant_id)
    st.write("Asistente recuperado con éxito:", assistant)
except Exception as e:
    st.error(f"Error al recuperar el asistente: {e}")

# Captura la entrada del usuario
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Crear un nuevo hilo con el mensaje del usuario
    try:
        thread = client.beta.threads.create(
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        st.write("Hilo creado con éxito:", thread)
    except Exception as e:
        st.error(f"Error al crear el hilo: {e}")

    # Ejecutar el hilo con el asistente
    try:
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )
        st.write("Hilo ejecutado con éxito:", run)
    except Exception as e:
        st.error(f"Error al ejecutar el hilo: {e}")
