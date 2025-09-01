import os
import streamlit as st
from dotenv import load_dotenv

# --- Setup ---
st.set_page_config(page_title="OpenAI Chat — Horseeman", layout="wide")
load_dotenv()

# --- Sidebar ---
st.sidebar.title("OpenAI Settings")
api_key = st.sidebar.text_input(
    "OPENAI_API_KEY",
    type="password",
    value=os.getenv("OPENAI_API_KEY", ""),
    help="Add in Streamlit → Settings → Secrets for Cloud",
)

model = st.sidebar.selectbox(
    "Model",
    ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-3.5-turbo"],
    index=0,
)

system_prompt = st.sidebar.text_area(
    "System prompt",
    value="You are a helpful, concise assistant.",
    help="Optional behavior steering",
    height=80,
)

clear = st.sidebar.button("🧹 Clear chat")
if clear:
    st.session_state.clear()
    st.rerun()

# --- Session state ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

# If system prompt changed mid-run, update the first message
if st.session_state.messages and st.session_state.messages[0]["role"] == "system":
    if st.session_state.messages[0]["content"] != system_prompt:
        st.session_state.messages[0]["content"] = system_prompt

st.title("🤖 OpenAI Chat")

# --- Render history ---
for m in st.session_state.messages:
    if m["role"] == "system":
        continue
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- Chat input ---
user_text = st.chat_input("Type your message…")
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        try:
            if not api_key:
                raise RuntimeError("Missing OPENAI_API_KEY")

            # New OpenAI SDK (>=1.x)
            from openai import OpenAI
            client = OpenAI(api_key=api_key)

            # Stream the response for snappy UX
            stream = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages,
                stream=True,
            )

            full = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    full += delta
                    placeholder.markdown(full)
            st.session_state.messages.append({"role": "assistant", "content": full or "…"})
        except Exception as e:
            placeholder.error(f"⚠️ OpenAI error: {e}")
