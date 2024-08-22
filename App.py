import openai
from openai import OpenAI
import streamlit as st

# Leer la API Key desde secrets
openai_api_key = st.secrets["openai_api_key"]
assistant_id = st.secrets["assistant_id"]
openai.organization = "org-XFlSAe5GkaZlemV7G7DZYiNy"
openai.project = "proj_No911gg9A3eaaNUjxKv3rwcE"

# Título de la aplicación
st.title("💬 Asistente Equipo Mantenimiento")
st.caption("🚀 Un asistente integrado en Streamlit")

# Inicializa el estado de los mensajes
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hola ¿En qué puedo ayudarte?"}]

# Muestra los mensajes existentes en la conversación
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Cliente de OpenAI con la API Key, organización y proyecto específicos
client = OpenAI(
  api_key=openai_api_key,
  organization="org-XFlSAe5GkaZlemV7G7DZYiNy",  # ID de tu organización
  project="proj_No911gg9A3eaaNUjxKv3rwcE"  # ID del proyecto por defecto
)

# Captura la entrada del usuario
if prompt := st.chat_input():
    # Agrega el mensaje del usuario al estado de la sesión
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Realiza la solicitud de completions
    response = client.chat.completions.create(
      model="gpt-4o-mini",  # Especifica el modelo aquí
      #assistant_id=assistant_id,  # si se confirma que es necesario
      messages=st.session_state.messages
    )

    # Obtén la respuesta del asistente y muéstrala en la aplicación
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
