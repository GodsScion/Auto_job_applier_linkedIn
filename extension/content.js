// Reason: Core logic — scans all visible form fields on the page,
// asks the local AI backend for answers, fills them, and handles file upload.
// Fixed: now also handles contenteditable divs (e.g. Snaphunt video resume form).

const FIELD_TYPES = ["input", "textarea", "select"];

// ── Label helpers ─────────────────────────────────────────────────────────────

function getLabel(el) {
  let contextParts = [];

  // 1. <label for="id">
  if (el.id) {
    const lbl = document.querySelector(`label[for="${el.id}"]`);
    if (lbl) contextParts.push(lbl.innerText.trim());
  }

  // 2. aria-label / placeholder / name / id
  const direct = el.getAttribute("aria-label") || el.placeholder || el.name || el.id;
  if (direct) contextParts.push(direct.trim());

  // 3. Nearest ancestor that has a visible heading/label sibling
  let node = el.parentElement;
  for (let i = 0; i < 5 && node; i++) {
    // Previous sibling text
    let sib = node.previousElementSibling;
    while (sib) {
      const txt = sib.innerText?.trim();
      if (txt && txt.length < 500) contextParts.push(txt);
      sib = sib.previousElementSibling;
    }
    // Label child inside parent container
    const lblChild = node.querySelector("label, h1, h2, h3, h4, h5, h6, [class*='label'], [class*='title']");
    if (lblChild) {
      const txt = lblChild.innerText?.trim();
      if (txt && txt.length < 500) contextParts.push(txt);
    }
    node = node.parentElement;
  }

  // Filter out empty or very short parts, and "unknown"
  const validContext = contextParts.filter(c => c && c.length > 1 && c.toLowerCase() !== "unknown");
  
  if (validContext.length > 0) {
    // Join them to give the AI maximum context, cap at 500 chars to prevent massive payloads
    // We reverse or just use them as is? The closest contexts (label, placeholder) are first, 
    // but the previous siblings are later. The AI can read it all.
    // Deduplicate array
    const uniqueContext = [...new Set(validContext)];
    return uniqueContext.join(" | ").substring(0, 600);
  }
  
  return "unknown";
}

// ── Field collection ──────────────────────────────────────────────────────────

function collectFields() {
  const fields = [];

  // Standard form elements
  FIELD_TYPES.forEach(tag => {
    document.querySelectorAll(tag).forEach(el => {
      if (el.offsetParent === null) return; // skip hidden
      if (["submit", "button", "reset", "hidden"].includes(el.type)) return;
      if (el.type === "file") {
        fields.push({ el, label: getLabel(el), type: "file" });
        return;
      }
      fields.push({
        el,
        label: getLabel(el),
        type: el.tagName === "SELECT" ? "select" : el.type || "text"
      });
    });
  });

  // ✅ FIX #1: contenteditable divs (Snaphunt-style rich text areas)
  document.querySelectorAll("[contenteditable='true'], [contenteditable='']").forEach(el => {
    if (el.offsetParent === null) return; // skip hidden
    if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") return; // already caught above
    fields.push({ el, label: getLabel(el), type: "contenteditable" });
  });

  return fields;
}

// ── Fill logic ────────────────────────────────────────────────────────────────

function fillField(el, value) {
  if (el.tagName === "SELECT") {
    [...el.options].forEach(opt => {
      if (opt.text.toLowerCase().includes(value.toLowerCase())) opt.selected = true;
    });
    el.dispatchEvent(new Event("change", { bubbles: true }));

  } else if (el.getAttribute("contenteditable") !== null) {
    // ✅ FIX #3: contenteditable divs need textContent, not .value
    el.focus();
    el.textContent = value;
    el.dispatchEvent(new Event("input",  { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
    // Some React/Vue frameworks listen to keyup too
    el.dispatchEvent(new KeyboardEvent("keyup", { bubbles: true }));

  } else if (el.tagName === "TEXTAREA" || el.tagName === "INPUT") {
    const nativeInputValueSetter =
      Object.getOwnPropertyDescriptor(
        el.tagName === "TEXTAREA"
          ? window.HTMLTextAreaElement.prototype
          : window.HTMLInputElement.prototype,
        "value"
      )?.set;
    nativeInputValueSetter?.call(el, value);
    el.dispatchEvent(new Event("input",  { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
  }
}

// ── Backend communication ─────────────────────────────────────────────────────

async function askBackend(backendUrl, fields) {
  const payload = fields
    .filter(f => f.type !== "file")
    .map(f => ({
      label: f.label,
      type: f.type,
      options: f.type === "select" ? [...f.el.options].map(o => o.text) : []
    }));

  const resp = await fetch(`${backendUrl}/fill`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fields: payload })
  });
  if (!resp.ok) throw new Error(`Backend error ${resp.status}`);
  return resp.json(); // { answers: [{label, value}] }
}

async function handleFileUpload(backendUrl, fileField) {
  const resp = await fetch(`${backendUrl}/resume`);
  if (!resp.ok) return;
  const blob = await resp.blob();
  const filename = resp.headers.get("X-Filename") || "resume.pdf";
  const file = new File([blob], filename, { type: blob.type });
  const dt = new DataTransfer();
  dt.items.add(file);
  fileField.el.files = dt.files;
  fileField.el.dispatchEvent(new Event("change", { bubbles: true }));
}

// ── Message listener ──────────────────────────────────────────────────────────

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.action !== "AUTO_APPLY") return;
  (async () => {
    try {
      const fields = collectFields();
      
      console.log("=== AUTO APPLY DEBUG: SCRAPED FIELDS ===");
      console.table(fields.map(f => ({ tag: f.el.tagName, type: f.type, label: f.label })));

      if (!fields.length) {
        console.warn("Auto Apply: No form fields found on page.");
        sendResponse({ success: false, error: "No form fields found" });
        return;
      }

      const fileFields = fields.filter(f => f.type === "file");
      const textFields = fields.filter(f => f.type !== "file");

      console.log("=== AUTO APPLY DEBUG: SENDING TO BACKEND ===");
      console.table(textFields.map(f => ({ label: f.label, type: f.type })));

      const { answers } = await askBackend(msg.backendUrl, textFields);
      
      console.log("=== AUTO APPLY DEBUG: RECEIVED FROM BACKEND ===");
      console.table(answers);
      let filled = 0;

      answers.forEach(({ label, value }) => {
        // ✅ FIX #2: fuzzy label matching — Snaphunt labels may have extra whitespace/caps
        const match = textFields.find(f =>
          f.label.trim().toLowerCase() === label.trim().toLowerCase()
        );
        if (match && value) {
          fillField(match.el, value);
          filled++;
        }
      });

      for (const ff of fileFields) await handleFileUpload(msg.backendUrl, ff);

      sendResponse({ success: true, filled });
    } catch (e) {
      sendResponse({ success: false, error: e.message });
    }
  })();
  return true; // keep channel open for async
});
