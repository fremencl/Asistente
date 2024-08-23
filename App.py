import openai
import streamlit as st
import time

# Leer la API Key y el assistant_id desde secrets
openai_api_key = st.secrets["openai_api_key"]
assistant_id = st.secrets["assistant_id"]

# Configuración de la pestaña del explorador
st.set_page_config(page_title="Asistente Mantenimiento", page_icon=":speech_balloon:")

# Configuración principal de la interfaz del chat
st.title("Asistente de Mantenimiento")
st.write("Herramienta de apoyo para resolver dudas de ubicaciones, equipos y órdenes")

# Crear un cliente de OpenAI
client = openai.Client(api_key=openai_api_key)

# Recuperar el asistente que quieres usar
try:
    assistant = client.beta.assistants.retrieve(assistant_id)
    st.write("Asistente recuperado con éxito:", assistant)
except Exception as e:
    st.error(f"Error al recuperar el asistente: {e}")

# Inicializar las variables de estado de la sesión para el control del chat
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

# Crear un hilo si aún no existe
if st.session_state.thread_id is None:
    try:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id
    except Exception as e:
        st.error(f"Error al crear el hilo: {e}")

# Inicializar la lista de mensajes si no existe en el estado de la sesión
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar los mensajes existentes en el chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capturar la entrada del usuario
if prompt := st.chat_input("¿Qué necesitas saber?"):
    # Agregar el mensaje del usuario al estado y mostrarlo
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Agregar el mensaje del usuario al hilo existente
    try:
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

        # Crear un run con instrucciones adicionales
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
            instructions="Please answer the queries using the knowledge provided."
        )

        # Aumentar el tiempo de espera para asegurar la finalización del run
        time.sleep(5)  # Aumentado el tiempo de espera a 5 segundos

        # Poll para verificar el estado del run
        while run.status != 'completed':
            time.sleep(5)  # Aumentado el tiempo de espera a 5 segundos
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )

        # Recuperar los mensajes generados por el asistente
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # Procesar y mostrar los mensajes del asistente
        assistant_messages_for_run = [
            message for message in messages
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            st.session_state.messages.append({"role": "assistant", "content": message.content[0].text})
            with st.chat_message("assistant"):
                st.markdown(message.content[0].text)

    except Exception as e:
        st.error(f"Error al enviar el mensaje: {e}")
