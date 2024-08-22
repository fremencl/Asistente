import openai
import streamlit as st
from openai.types.beta.assistant_stream_event import (
    ThreadRunStepCreated,
    ThreadRunStepDelta,
    ThreadRunStepCompleted,
    ThreadMessageCreated,
    ThreadMessageDelta
    )
from openai.types.beta.threads.text_delta_block import TextDeltaBlock

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
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], str):
            st.markdown(msg["content"])
        elif isinstance(msg["content"], list):
            for item in msg["content"]:
                item_type = item.get("type")
                if item_type == "text":
                    st.markdown(item["content"])
                elif item_type == "code_input" or item_type == "code_output":
                    st.code(item["content"])
                elif item_type == "image":
                    st.image(item["content"])

# Captura la entrada del usuario
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Crear un nuevo hilo con el mensaje del usuario
    try:
        if st.session_state["thread_id"] is None:
            thread = client.beta.threads.create()
            st.session_state["thread_id"] = thread.id
            st.write("Hilo creado con éxito:", thread)
        else:
            thread = client.beta.threads.retrieve(st.session_state["thread_id"])

        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt
        )
        st.write("Mensaje del usuario añadido al hilo con éxito.")
    except Exception as e:
        st.error(f"Error al crear o actualizar el hilo: {e}")

    # Ejecutar el hilo con el asistente y obtener la respuesta
    try:
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )
        st.write("Ejecutando el asistente...")

        # Procesar el resultado final aquí
        assistant_output = []

        for event in run:
            if isinstance(event, ThreadMessageCreated):
                assistant_output.append({"type": "text", "content": ""})
                st.empty()

            elif isinstance(event, ThreadMessageDelta):
                if isinstance(event.data.delta.content[0], TextDeltaBlock):
                    assistant_output[-1]["content"] += event.data.delta.content[0].text.value
                    st.markdown(assistant_output[-1]["content"])

        st.session_state.messages.append({"role": "assistant", "content": assistant_output})

    except Exception as e:
        st.error(f"Error al ejecutar el hilo con el asistente: {e}")
