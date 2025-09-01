import streamlit as st
import requests
import os
import streamlit.components.v1 as components

with open("ui/matrix_rain.html", "r") as f:
    matrix_html = f.read()

components.html(matrix_html, height=0, width=0)


st.set_page_config(page_title="Headless ChatGPT", layout="wide", initial_sidebar_state="expanded")

st.sidebar.title("Backend")
backend = st.sidebar.selectbox("Choose backend", ["Headless", "OpenAI API"])
url = st.sidebar.text_input("Backend URL", "http://localhost:3001/queryAi")

st.title("Headless ChatGPT UI")

prompt = st.text_area("Your prompt", height=200)
if st.button("Send"):
    if backend == "Headless":
        response = requests.post(url, json={"prompt": prompt})
        st.json(response.json())
    else:
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")
        res = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "user", "content": prompt}])
        st.write(res.choices[0].message["content"])
