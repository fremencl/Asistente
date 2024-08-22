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

# Inicializar el estado de sesión
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hola ¿En qué puedo ayudarte?"}]
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = None

# Muestra los mensajes existentes en la conversación
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Captura la entrada del usuario
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Crear un nuevo hilo si no existe
    if not st.session_state.thread_id:
        try:
            thread = client.beta.threads.create()
            st.session_state.thread_id = thread.id
            st.write(f"Hilo creado con éxito: {st.session_state.thread_id}")
        except Exception as e:
            st.error(f"Error al crear el hilo: {e}")

    # Añadir el mensaje del usuario al hilo existente
    try:
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt,
        )
        st.write("Mensaje del usuario añadido al hilo con éxito.")
    except Exception as e:
        st.error(f"Error al añadir el mensaje al hilo: {e}")

    # Ejecutar el hilo con el asistente utilizando streaming
    try:
        st.write("Ejecutando el asistente...")
        with client.beta.threads.runs.stream(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant.id,
            event_handler=None  # Aquí podrías personalizar un EventHandler si lo deseas
        ) as stream:
            response_content = ""
            for event in stream:
                if event.type == "text":
                    response_content += event.text
                    st.chat_message("assistant").write(event.text)  # Mostrar la respuesta en tiempo real

            # Guardar la respuesta completa en la sesión
            st.session_state.messages.append({"role": "assistant", "content": response_content})
            st.write("Asistente finalizó la ejecución con éxito.")
    except Exception as e:
        st.error(f"Error al ejecutar el hilo con el asistente: {e}")
