# Headless ChatGPT Streamlit UI

Streamlit UI for controlling ChatGPT via Puppeteer-based headless server or OpenAI API.

## Quickstart

```bash
git clone https://github.com/YOUR_USERNAME/headless-chatgpt-streamlit
cd headless-chatgpt-streamlit
npm install --prefix node-server
pip install -r requirements.txt
```

### Run locally

```bash
# Start the Node bridge (headless ChatGPT)
cd node-server
npm start

# In another terminal
streamlit run ui/main.py
```

Switch between headless mode or OpenAI API via sidebar.
