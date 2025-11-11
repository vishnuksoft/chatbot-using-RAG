const API = (path) => `http://localhost:8000${path}`;

let state = {
  userId: document.getElementById("userId").value,
  chatId: null,
  sessions: [],
};

const el = (id) => document.getElementById(id);
const messages = el("messages");

function addMsg(role, content) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.innerHTML = content.replace(/\n/g, "<br/>");
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

async function startChat() {
  const res = await fetch(API("/chat/start"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: state.userId, title: "New Chat" }),
  });
  const data = await res.json();
  state.chatId = data.chat_id;
  el("chatHeader").textContent = `Chat: ${state.chatId.slice(0, 8)}…`;
  renderSessions();
}

// async function sendMessage(text) {
//   addMsg("user", text);
//   const res = await fetch(API("/chat/message"), {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({
//       user_id: state.userId,
//       chat_id: state.chatId,
//       message: text,
//     }),
//   });
//   const data = await res.json();
//   //   const citeLine = data.citations && data.citations.length ?
//   //     `<br><small>Sources: ${data.citations.filter(Boolean).map((c,i)=>`[${i+1}] ${c}`).join('  ·  ')}</small>` : '';
//   const uniqueCites = [...new Set(data.citations || [])].filter(Boolean);
//   const citeLine = uniqueCites.length
//     ? `<br><small>Sources: ${uniqueCites.join(" · ")}</small>`
//     : "";
//   addMsg("assistant", data.answer + citeLine);
// }

async function sendMessage(text) {
  addMsg("user", text);

  const res = await fetch(API("/chat/message"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: state.userId,
      chat_id: state.chatId,
      message: text,
    }),
  });

  const data = await res.json();

  // 🧹 Remove [1], [2], etc. from the LLM answer
  const cleanAnswer = (data.answer || "").replace(/\[\d+\]/g, "").trim();

  // 🧹 Skip all sources/citations
  addMsg("assistant", cleanAnswer);
}


function renderSessions() {
  const list = el("sessions");
  const item = document.createElement("div");
  item.className = "session-item active";
  item.textContent = `Session ${state.chatId.slice(0, 8)}…`;
  item.onclick = () => {};
  list.innerHTML = "";
  list.appendChild(item);
}

el("newChatBtn").onclick = async () => {
  state.userId = el("userId").value.trim() || "demo-user";
  await startChat();
  messages.innerHTML = "";
};

el("msgForm").onsubmit = async (e) => {
  e.preventDefault();
  if (!state.chatId) await startChat();
  const txt = el("msgInput").value.trim();
  if (!txt) return;
  el("msgInput").value = "";
  sendMessage(txt);
};

el("uploadForm").onsubmit = async (e) => {
  e.preventDefault();
  const files = el("files").files;
  if (!files.length) return;
  const fd = new FormData();
  for (const f of files) fd.append("files", f);
  fd.append("user_id", el("userId").value.trim() || "demo-user");
  const res = await fetch(API("/ingest/upload"), { method: "POST", body: fd });
  const data = await res.json();
  alert(`Inserted ${data.inserted} chunks`);
};

el("urlForm").onsubmit = async (e) => {
  e.preventDefault();
  const url = el("urlInput").value.trim();
  if (!url) return;
  const fd = new FormData();
  fd.append("url", url);
  fd.append("user_id", el("userId").value.trim() || "demo-user");
  const res = await fetch(API("/ingest/url"), { method: "POST", body: fd });
  const data = await res.json();
  alert(`Inserted ${data.inserted} chunks`);
  el("urlInput").value = "";
};

// initialize
startChat();
