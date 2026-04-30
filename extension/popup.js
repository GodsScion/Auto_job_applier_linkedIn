// Reason: Loads saved backend URL, wires up the single-click apply button,
// and relays the trigger to the active tab's content script.

const urlInput = document.getElementById("backend-url");
const applyBtn = document.getElementById("apply-btn");
const status   = document.getElementById("status");

// Restore saved backend URL from storage
chrome.storage.local.get("backendUrl", ({ backendUrl }) => {
  if (backendUrl) urlInput.value = backendUrl;
});

// Persist URL on change
urlInput.addEventListener("change", () => {
  chrome.storage.local.set({ backendUrl: urlInput.value.trim() });
});

applyBtn.addEventListener("click", async () => {
  const backendUrl = urlInput.value.trim();
  if (!backendUrl) {
    setStatus("Enter backend URL first", "err");
    return;
  }
  chrome.storage.local.set({ backendUrl });

  applyBtn.disabled = true;
  setStatus("Scanning page…");

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  chrome.tabs.sendMessage(tab.id, { action: "AUTO_APPLY", backendUrl }, (res) => {
    applyBtn.disabled = false;
    if (chrome.runtime.lastError) {
      setStatus("Content script not ready — reload page", "err");
      return;
    }
    if (res?.success) setStatus(`✅ Filled ${res.filled} field(s)`, "ok");
    else setStatus(`❌ ${res?.error || "Unknown error"}`, "err");
  });
});

function setStatus(msg, cls = "") {
  status.textContent = msg;
  status.className = cls;
}
