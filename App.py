from openai import OpenAI
import streamlit as st

# Leer la API Key y el ID del asistente desde secrets
openai_api_key = st.secrets["openai_api_key"]
assistant_id = st.secrets["assistant_id"]

# Título de la aplicación
st.title("💬 Asistente Equipo Mantenimiento")
st.caption("🚀 Un asistente personalizado integrado en Streamlit")

# Inicializa el estado de los mensajes
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hola ¿En qué puedo ayudarte?"}]

# Muestra los mensajes existentes en la conversación
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Cliente de OpenAI con la API Key
client = OpenAI(api_key=openai_api_key)

# Captura la entrada del usuario
if prompt := st.chat_input():
    # Agrega el mensaje del usuario al estado de la sesión
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Realiza la solicitud al asistente personalizado
    response = client.chat.completions.create(
      messages=st.session_state.messages,
      assistant_id=assistant_id  # ID del asistente personalizado
    )

    # Obtén la respuesta del asistente y muéstrala en la aplicación
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
