const form = document.getElementById("chatForm");
const input = document.getElementById("messageInput");
const messages = document.getElementById("messages");
const clearBtn = document.getElementById("clearBtn");

function addMessage(text, role) {
  const el = document.createElement("div");
  el.className = `message ${role}`;
  // Text is inserted as text, not HTML, to avoid rendering untrusted API content.
  el.textContent = text;
  messages.appendChild(el);
  messages.scrollTop = messages.scrollHeight;
}

async function sendMessage(text) {
  addMessage(text, "user");
  const pending = document.createElement("div");
  pending.className = "message bot";
  pending.textContent = "Sedang mencari informasi...";
  messages.appendChild(pending);
  messages.scrollTop = messages.scrollHeight;
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message: text})
    });
    const data = await response.json();
    pending.remove();
    addMessage(data.reply || data.error || "Tidak ada jawaban.", "bot");
  } catch (error) {
    pending.remove();
    addMessage("Tidak dapat menghubungi server. Pastikan Flask sedang berjalan.", "bot");
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  await sendMessage(text);
});
document.querySelectorAll(".suggestion").forEach(button => {
  button.addEventListener("click", () => sendMessage(button.dataset.message));
});
clearBtn.addEventListener("click", () => {
  messages.innerHTML = "";
  addMessage("Percakapan di tampilan dibersihkan. Riwayat tersimpan di database lokal.", "bot");
});
