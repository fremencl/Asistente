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

    # Ejecutar el hilo con el asistente
    try:
        with client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=assistant.id,
            tool_choice={"type": "code_interpreter"},
            stream=True
        ) as stream:
            st.write("Ejecutando el asistente...")

            assistant_output = []

            for event in stream:
                if isinstance(event, ThreadRunStepCreated):
                    if event.data.step_details.type == "tool_calls":
                        assistant_output.append({"type": "code_input", "content": ""})
                        code_input_block = st.status("Escribiendo código ⏳ ...", expanded=True).empty()

                if isinstance(event, ThreadRunStepDelta):
                    if event.data.delta.step_details.tool_calls[0].code_interpreter is not None:
                        code_interpreter = event.data.delta.step_details.tool_calls[0].code_interpreter
                        code_input_delta = code_interpreter.input
                        if code_input_delta:
                            assistant_output[-1]["content"] += code_input_delta
                            code_input_block.code(assistant_output[-1]["content"])

                elif isinstance(event, ThreadRunStepCompleted):
                    # Procesar el resultado final aquí, similar a cómo se maneja en el código de referencia

                elif isinstance(event, ThreadMessageCreated):
                    assistant_output.append({"type": "text", "content": ""})
                    assistant_text_box = st.empty()

                elif isinstance(event, ThreadMessageDelta):
                    if isinstance(event.data.delta.content[0], TextDeltaBlock):
                        assistant_text_box.markdown(event.data.delta.content[0].text.value)
                        assistant_output[-1]["content"] += event.data.delta.content[0].text.value

            st.session_state.messages.append({"role": "assistant", "content": assistant_output})

    except Exception as e:
        st.error(f"Error al ejecutar el hilo con el asistente: {e}")
