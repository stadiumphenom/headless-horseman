# ui/main.py
import os
import json
import requests
import streamlit as st
import streamlit.components.v1 as components

# ---- Streamlit setup FIRST ----
st.set_page_config(
    page_title="Headless ChatGPT",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Optional background effect ----
try:
    with open("ui/matrix_rain.html", "r", encoding="utf-8") as f:
        components.html(f.read(), height=0, width=0)
except Exception:
    pass  # don't crash if the file isn't present

st.title("🤖 Headless ChatGPT UI")

# ---- Sidebar controls ----
st.sidebar.title("Backend")
backend = st.sidebar.selectbox("Choose backend", ["Headless", "OpenAI API"], index=0)

default_url = os.getenv("HEADLESS_URL", "http://localhost:3001")
url_base = st.sidebar.text_input("Headless server base URL", default_url)
query_endpoint = url_base.rstrip("/") + "/queryAi"
health_endpoint = url_base.rstrip("/") + "/health"

colA, colB = st.sidebar.columns(2)
with colA:
    if st.button("🩺 Health Check"):
        try:
            r = requests.get(health_endpoint, timeout=10)
            st.sidebar.success(f"/health → {r.status_code} {r.text[:120]}")
        except requests.RequestException as e:
            st.sidebar.error(f"Health check failed: {e}")

with colB:
    timeout_s = st.number_input("Timeout (s)", min_value=5, max_value=300, value=60, step=5)

# Model pickers / keys
if backend == "OpenAI API":
    model = st.sidebar.selectbox(
        "Model",
        ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-3.5-turbo", "gpt-4-turbo"],
        index=0,
    )
    user_key = st.sidebar.text_input(
        "OPENAI_API_KEY",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="Set this in Streamlit secrets or env var OPENAI_API_KEY",
    )
else:
    # headless bridge may accept a model name too
    model = st.sidebar.text_input("Model (optional for headless)", value="gpt-4o-mini")

st.divider()

# ---- Chat input ----
prompt = st.text_area("Your prompt", height=200, placeholder="Type your prompt here...")

send_col, clear_col = st.columns([1, 1])
send_clicked = send_col.button("Send", type="primary")
if clear_col.button("Clear output"):
    st.session_state.pop("last_response", None)
    st.rerun()

# ---- Actions ----
def call_headless(prompt_text: str) -> dict:
    payload = {"prompt": prompt_text, "model": model, "newChatIfMissing": True}
    r = requests.post(query_endpoint, json=payload, timeout=timeout_s)
    r.raise_for_status()
    # some bridges return text, some json
    try:
        return r.json()
    except ValueError:
        return {"answer": r.text}

def call_openai(prompt_text: str, model_name: str, api_key: str) -> str:
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY")

    # Prefer the new SDK if present
    try:
        from openai import OpenAI  # openai>=1.x
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt_text}],
        )
        return resp.choices[0].message.content
    except Exception as e_new:
        # Fallback to legacy sdk if installed
        try:
            import openai  # legacy
            openai.api_key = api_key
            resp = openai.ChatCompletion.create(
                model=model_name,
                messages=[{"role": "system", "content": "You are a helpful assistant."},
                          {"role": "user", "content": prompt_text}],
            )
            return resp.choices[0].message["content"]
        except Exception as e_old:
            raise RuntimeError(f"OpenAI call failed. New SDK error: {e_new}; Legacy error: {e_old}")

if send_clicked:
    if not prompt.strip():
        st.error("Please enter a prompt.")
    else:
        with st.status("Working...", expanded=True):
            try:
                if backend == "Headless":
                    data = call_headless(prompt.strip())
                    st.session_state["last_response"] = data
                else:
                    text = call_openai(prompt.strip(), model, user_key)
                    st.session_state["last_response"] = {"answer": text}
            except requests.exceptions.ConnectionError as e:
                st.error(
                    "Cannot reach the headless server.\n\n"
                    "• If running on Streamlit Cloud, `localhost` won't work.\n"
                    "• Deploy your Node/Playwright bridge to a public URL and set it above.\n"
                    f"Raw error: {e}"
                )
            except Exception as e:
                st.error(f"Error: {e}")

# ---- Output ----
resp = st.session_state.get("last_response")
if resp:
    st.subheader("Response")
    # show both JSON and extracted text if present
    if isinstance(resp, dict):
        text = resp.get("answer") or resp.get("text")
        if text:
            st.write(text)
        with st.expander("Raw JSON"):
            st.code(json.dumps(resp, indent=2))
    else:
        st.write(str(resp))
