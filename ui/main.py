import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="OpenAI Chat", layout="wide")

# Pull from Streamlit secrets
api_key = st.secrets["OPENAI_API_KEY"]

client = OpenAI(api_key=api_key)

# Session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]

st.title("🤖 OpenAI Chat")

# Render history
for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

# Input
if prompt := st.chat_input("Type your message…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full = ""
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                full += delta
                placeholder.markdown(full)
        st.session_state.messages.append({"role": "assistant", "content": full})
