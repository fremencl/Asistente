import openai
import streamlit as st

# Leer la API Key y el assistant_id desde secrets
openai_api_key = st.secrets["openai_api_key"]
assistant_id = st.secrets["assistant_id"]

# Crear un cliente de OpenAI
client = openai.Client(api_key=openai_api_key)

# Recuperar el asistente que quieres usar
assistant = client.beta.assistants.retrieve(assistant_id)

# Título de la aplicación
st.title("💬 Asistente Equipo Mantenimiento")
st.caption("🚀 Un asistente integrado en Streamlit")

# Inicializa el estado de los mensajes
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hola ¿En qué puedo ayudarte?"}]

# Muestra los mensajes existentes en la conversación
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Captura la entrada del usuario
if prompt := st.chat_input():
    # Agrega el mensaje del usuario al estado de la sesión
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Crear un nuevo hilo con el mensaje del usuario
    thread = client.beta.threads.create(
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Ejecutar el hilo con el asistente
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    # Obtener la respuesta del asistente
    response = client.beta.threads.messages.list(thread_id=thread.id)
    msg = response.data[0].content[0].text.value

    # Agregar la respuesta al estado de la sesión
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
