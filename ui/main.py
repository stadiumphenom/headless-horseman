# ui/main.py
import os
import io
import csv
import json
import datetime as dt
import streamlit as st
from openai import OpenAI

# ------------- App setup -------------
st.set_page_config(page_title="PRIMUS — Signal Chat", layout="wide")

# background (matrix rain) – loads an external HTML file if present
try:
    import streamlit.components.v1 as components
    with open("ui/matrix_rain.html", "r", encoding="utf-8") as f:
        components.html(f.read(), height=200, width=0)  # fixed canvas behind the app
except Exception:
    pass

# ------------- Secrets / client -------------
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("Missing OPENAI_API_KEY in .streamlit/secrets.toml (local) or App → Settings → Secrets (cloud).")
    st.stop()

client = OpenAI(api_key=api_key)

# ------------- Sidebar controls -------------
st.sidebar.markdown("### ⚙️ Session")
if st.sidebar.button("🧹 New Chat"):
    st.session_state.clear()
    st.rerun()

st.sidebar.markdown("### 🧠 Model & Params")
model = st.sidebar.selectbox(
    "Model",
    ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-3.5-turbo"],
    index=0,
)
temperature = st.sidebar.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
max_tokens = st.sidebar.slider("Max tokens", 128, 8192, 1024, 64)

system_prompt = st.sidebar.text_area(
    "System prompt",
    value="You are PRIMUS: concise, capable, a little snarky when warranted, but always helpful.",
    height=150,
)

# ------------- Session state -------------
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
# keep system prompt live-updated
if st.session_state.messages and st.session_state.messages[0]["role"] == "system":
    st.session_state.messages[0]["content"] = system_prompt

if "run_id" not in st.session_state:
    st.session_state.run_id = dt.datetime.utcnow().strftime("%Y%m%d-%H%M%S")

# ------------- Title -------------
st.markdown("""
<h1 style="display:flex;align-items:center;gap:.5rem;">
  <span style="font-size:1.8rem;">🜲</span> PRIMUS — Signal Chat
</h1>
""", unsafe_allow_html=True)

# ------------- History render -------------
def render_history():
    for m in st.session_state.messages:
        if m["role"] == "system":
            continue
        avatar = "🧑‍💻" if m["role"] == "user" else "🤖"
        with st.chat_message(m["role"], avatar=avatar):
            st.markdown(m["content"])

render_history()

# ------------- Chat input -------------
user_text = st.chat_input("Type your message…")
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_text)

    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full = ""
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    full += delta
                    placeholder.markdown(full)
        except Exception as e:
            full = f"⚠️ OpenAI error: {e}"
            placeholder.error(full)
        st.session_state.messages.append({"role": "assistant", "content": full})

# ------------- Exports -------------
st.divider()
st.subheader("Exports")

def export_json(messages) -> bytes:
    # redact system prompt if you want; leaving intact by default
    payload = {
        "run_id": st.session_state.run_id,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": messages,
        "exported_at_utc": dt.datetime.utcnow().isoformat() + "Z",
    }
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")

def export_csv(messages) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["idx", "role", "content"])
    for i, m in enumerate(messages):
        if m["role"] == "system":  # keep or skip; here we keep
            pass
        writer.writerow([i, m["role"], m["content"].replace("\n", "\\n")])
    return buf.getvalue().encode("utf-8")

col1, col2 = st.columns(2)
with col1:
    st.download_button(
        "⬇️ Download JSON",
        data=export_json(st.session_state.messages),
        file_name=f"primus_chat_{st.session_state.run_id}.json",
        mime="application/json",
        use_container_width=True,
    )
with col2:
    st.download_button(
        "⬇️ Download CSV",
        data=export_csv(st.session_state.messages),
        file_name=f"primus_chat_{st.session_state.run_id}.csv",
        mime="text/csv",
        use_container_width=True,
    )
