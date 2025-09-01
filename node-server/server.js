const express = require("express");
const cors = require("cors");
const bodyParser = require("body-parser");

const { start, query, retry, newChat, selectChat, getCurrentChatList, getCurrentGptList } = require("headless-chatgpt");

const app = express();
const port = 3001;

app.use(cors());
app.use(bodyParser.json());

let browserInstance = null;

app.get("/start", async (req, res) => {
  try {
    browserInstance = await start();
    res.json({ status: "Browser started" });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post("/queryAi", async (req, res) => {
  try {
    const { prompt } = req.body;
    if (!prompt) return res.status(400).json({ error: "Missing prompt" });

    const result = await query(prompt);
    res.json({ result });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post("/retry", async (req, res) => {
  try {
    const result = await retry();
    res.json({ result });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post("/newChat", async (req, res) => {
  try {
    const result = await newChat();
    res.json({ result });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post("/selectChat", async (req, res) => {
  try {
    const { chatId } = req.body;
    const result = await selectChat(chatId);
    res.json({ result });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get("/currentChatList", async (req, res) => {
  try {
    const result = await getCurrentChatList();
    res.json({ chats: result });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get("/currentGptList", async (req, res) => {
  try {
    const result = await getCurrentGptList();
    res.json({ models: result });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(port, () => {
  console.log(`🤖 Headless ChatGPT bridge listening on http://localhost:${port}`);
});
