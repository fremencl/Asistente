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

# Inicializa el estado de los mensajes
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hola ¿En qué puedo ayudarte?"}]

# Muestra los mensajes existentes en la conversación
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

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

    # Obtener la respuesta del asistente
    try:
        messages = client.beta.threads.messages.list(thread_id=thread.id).data
        st.write("Mensajes obtenidos del hilo:", messages)
        
        # Usar el enfoque del código de referencia para extraer y mostrar la respuesta
        if messages and messages[0].content:
            response_text = messages[0].content[0].text.value
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            st.chat_message("assistant").write(response_text)
            st.write("Respuesta del asistente obtenida con éxito:", response_text)
        else:
            st.error("No se pudo obtener una respuesta del asistente.")
    except Exception as e:
        st.error(f"Error al obtener el mensaje del asistente: {e}")
