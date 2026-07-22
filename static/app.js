/**
 * Image Caption Generator — frontend application logic.
 * No build step, no frameworks: plain modern JavaScript (ES2020+).
 */
(() => {
  "use strict";

  // ---------------------------------------------------------------------
  // Element references
  // ---------------------------------------------------------------------
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("fileInput");
  const browseBtn = document.getElementById("browseBtn");
  const cameraBtn = document.getElementById("cameraBtn");
  const clearBtn = document.getElementById("clearBtn");
  const previewImage = document.getElementById("previewImage");
  const viewfinder = document.getElementById("viewfinder");

  const modeSelect = document.getElementById("modeSelect");
  const toneSelect = document.getElementById("toneSelect");
  const languageSelect = document.getElementById("languageSelect");
  const streamToggle = document.getElementById("streamToggle");

  const generateBtn = document.getElementById("generateBtn");
  const generateHint = document.getElementById("generateHint");

  const results = document.getElementById("results");
  const streamCard = document.getElementById("streamCard");
  const streamOutput = document.getElementById("streamOutput");

  const captionLabel = document.getElementById("captionLabel");
  const captionText = document.getElementById("captionText");
  const detailedBlock = document.getElementById("detailedBlock");
  const detailedText = document.getElementById("detailedText");
  const altBlock = document.getElementById("altBlock");
  const altText = document.getElementById("altText");
  const tagsRow = document.getElementById("tagsRow");
  const confidenceFill = document.getElementById("confidenceFill");
  const confidenceValue = document.getElementById("confidenceValue");
  const downloadBtn = document.getElementById("downloadBtn");

  const historyList = document.getElementById("historyList");
  const refreshHistoryBtn = document.getElementById("refreshHistoryBtn");

  const statusBanner = document.getElementById("statusBanner");
  const statusBannerText = document.getElementById("statusBannerText");

  const themeToggle = document.getElementById("themeToggle");
  const themeIconSun = document.getElementById("themeIconSun");
  const themeIconMoon = document.getElementById("themeIconMoon");

  const toast = document.getElementById("toast");

  // ---------------------------------------------------------------------
  // State
  // ---------------------------------------------------------------------
  let selectedFile = null;
  let lastResult = null;
  let lastHistoryId = null;
  let cameraStream = null;

  // ---------------------------------------------------------------------
  // Theme (dark mode)
  // ---------------------------------------------------------------------
  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    themeIconSun.style.display = theme === "dark" ? "none" : "block";
    themeIconMoon.style.display = theme === "dark" ? "block" : "none";
    localStorage.setItem("icg-theme", theme);
  }

  function initTheme() {
    const stored = localStorage.getItem("icg-theme");
    if (stored) {
      applyTheme(stored);
      return;
    }
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    applyTheme(prefersDark ? "dark" : "light");
  }

  themeToggle.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme");
    applyTheme(current === "dark" ? "light" : "dark");
  });

  // ---------------------------------------------------------------------
  // Toast helper
  // ---------------------------------------------------------------------
  let toastTimer = null;
  function showToast(message) {
    toast.textContent = message;
    toast.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("is-visible"), 2400);
  }

  function showBanner(message) {
    statusBannerText.textContent = message;
    statusBanner.classList.add("is-visible");
  }

  function hideBanner() {
    statusBanner.classList.remove("is-visible");
  }

  // ---------------------------------------------------------------------
  // File selection
  // ---------------------------------------------------------------------
  const ALLOWED_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);
  const MAX_BYTES = 8 * 1024 * 1024;

  function setSelectedFile(file) {
    if (!file) return;
    if (!ALLOWED_TYPES.has(file.type)) {
      showToast("Unsupported format. Please use JPEG, PNG, or WEBP.");
      return;
    }
    if (file.size > MAX_BYTES) {
      showToast("Image is too large. Maximum size is 8 MB.");
      return;
    }
    selectedFile = file;
    const url = URL.createObjectURL(file);
    previewImage.src = url;
    previewImage.alt = `Preview of ${file.name}`;
    previewImage.classList.add("is-visible");
    dropZone.classList.add("has-image");
    clearBtn.style.display = "inline-flex";
    generateBtn.disabled = false;
    generateHint.textContent = file.name;
    results.classList.remove("is-visible");
  }

  browseBtn.addEventListener("click", () => fileInput.click());
  dropZone.addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", (event) => {
    const file = event.target.files && event.target.files[0];
    setSelectedFile(file);
  });

  ["dragenter", "dragover"].forEach((evtName) => {
    dropZone.addEventListener(evtName, (event) => {
      event.preventDefault();
      dropZone.classList.add("is-dragover");
    });
  });

  ["dragleave", "drop"].forEach((evtName) => {
    dropZone.addEventListener(evtName, (event) => {
      event.preventDefault();
      dropZone.classList.remove("is-dragover");
    });
  });

  dropZone.addEventListener("drop", (event) => {
    const file = event.dataTransfer.files && event.dataTransfer.files[0];
    setSelectedFile(file);
  });

  clearBtn.addEventListener("click", (event) => {
    event.stopPropagation();
    selectedFile = null;
    fileInput.value = "";
    previewImage.src = "";
    previewImage.classList.remove("is-visible");
    dropZone.classList.remove("has-image");
    clearBtn.style.display = "none";
    generateBtn.disabled = true;
    generateHint.textContent = "Select an image to get started.";
    results.classList.remove("is-visible");
  });

  // ---------------------------------------------------------------------
  // Camera capture
  // ---------------------------------------------------------------------
  async function captureFromCamera() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      showToast("Camera access is not supported in this browser.");
      return;
    }
    try {
      cameraStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
    } catch (err) {
      showToast("Camera permission was denied.");
      return;
    }

    const video = document.createElement("video");
    video.srcObject = cameraStream;
    video.playsInline = true;
    await video.play();

    // Give the stream a brief moment to size correctly before capture.
    await new Promise((resolve) => setTimeout(resolve, 350));

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth || 1280;
    canvas.height = video.videoHeight || 720;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    cameraStream.getTracks().forEach((track) => track.stop());
    cameraStream = null;

    canvas.toBlob(
      (blob) => {
        if (!blob) {
          showToast("Could not capture an image from the camera.");
          return;
        }
        const file = new File([blob], `camera-capture-${Date.now()}.jpg`, { type: "image/jpeg" });
        setSelectedFile(file);
      },
      "image/jpeg",
      0.92
    );
  }

  cameraBtn.addEventListener("click", captureFromCamera);

  // ---------------------------------------------------------------------
  // Generate caption
  // ---------------------------------------------------------------------
  function renderResult(result) {
    lastResult = result;
    const mode = modeSelect.value;

    captionLabel.textContent = mode === "accessibility" ? "Alt text" : "Caption";
    captionText.textContent = result.caption || "—";

    if (result.detailed_description) {
      detailedText.textContent = result.detailed_description;
      detailedBlock.style.display = "block";
    } else {
      detailedBlock.style.display = "none";
    }

    altText.textContent = result.alt_text || "—";

    tagsRow.innerHTML = "";
    (result.tags || []).forEach((tag) => {
      const span = document.createElement("span");
      span.className = "tag";
      span.textContent = tag;
      tagsRow.appendChild(span);
    });
    if (result.mood) {
      const span = document.createElement("span");
      span.className = "tag";
      span.textContent = `mood: ${result.mood}`;
      tagsRow.appendChild(span);
    }

    const pct = Math.round((result.confidence || 0) * 100);
    confidenceFill.style.width = `${pct}%`;
    confidenceValue.textContent = `${pct}%`;

    results.classList.add("is-visible");
  }

  async function readSseStream(response, onChunk) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const events = buffer.split("\n\n");
      buffer = events.pop() || "";

      for (const evt of events) {
        const lines = evt.split("\n");
        const eventLine = lines.find((l) => l.startsWith("event:"));
        const dataLine = lines.find((l) => l.startsWith("data:"));
        const eventType = eventLine ? eventLine.replace("event:", "").trim() : "message";
        const data = dataLine ? dataLine.replace("data:", "").trim() : "";

        if (eventType === "error") {
          throw new Error(data || "Streaming failed.");
        }
        if (eventType === "done") {
          return;
        }
        onChunk(data.replace(/\\n/g, "\n"));
      }
    }
  }

  async function generateCaption() {
    if (!selectedFile) return;

    hideBanner();
    generateBtn.disabled = true;
    viewfinder.classList.add("is-scanning");
    streamOutput.textContent = "";
    streamCard.style.display = streamToggle.checked ? "block" : "none";
    results.classList.remove("is-visible");

    const mode = modeSelect.value;
    const tone = toneSelect.value;
    const language = languageSelect.value;

    try {
      if (streamToggle.checked) {
        const streamForm = new FormData();
        streamForm.append("file", selectedFile);
        const streamResponse = await fetch(
          `/api/caption/stream?mode=${mode}&tone=${tone}&language=${language}`,
          { method: "POST", body: streamForm }
        );
        if (!streamResponse.ok) {
          throw new Error(`Streaming request failed (${streamResponse.status}).`);
        }
        results.classList.add("is-visible");
        await readSseStream(streamResponse, (chunk) => {
          streamOutput.textContent += chunk;
        });
      }

      const form = new FormData();
      form.append("file", selectedFile);
      const response = await fetch(`/api/caption?mode=${mode}&tone=${tone}&language=${language}`, {
        method: "POST",
        body: form,
      });

      if (!response.ok) {
        const errBody = await response.json().catch(() => ({}));
        throw new Error(errBody.error || `Request failed with status ${response.status}.`);
      }

      const data = await response.json();
      renderResult(data);
      showToast("Caption generated.");
      loadHistory();
    } catch (err) {
      showBanner(err.message || "Something went wrong while generating the caption.");
    } finally {
      generateBtn.disabled = false;
      viewfinder.classList.remove("is-scanning");
    }
  }

  generateBtn.addEventListener("click", generateCaption);

  // ---------------------------------------------------------------------
  // Copy / download
  // ---------------------------------------------------------------------
  document.querySelectorAll("[data-copy-target]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const targetId = btn.getAttribute("data-copy-target");
      const text = document.getElementById(targetId).textContent;
      try {
        await navigator.clipboard.writeText(text);
        showToast("Copied to clipboard.");
      } catch {
        showToast("Could not copy automatically. Please select and copy manually.");
      }
    });
  });

  downloadBtn.addEventListener("click", () => {
    if (!lastResult) return;
    const lines = [
      `Caption: ${lastResult.caption}`,
      lastResult.detailed_description ? `\nDetailed description:\n${lastResult.detailed_description}` : "",
      `\nAlt text:\n${lastResult.alt_text}`,
      lastResult.tags && lastResult.tags.length ? `\nTags: ${lastResult.tags.join(", ")}` : "",
      lastResult.mood ? `\nMood: ${lastResult.mood}` : "",
    ];
    const blob = new Blob([lines.join("\n")], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "caption.txt";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  });

  // ---------------------------------------------------------------------
  // History
  // ---------------------------------------------------------------------
  function formatDate(isoString) {
    try {
      return new Date(isoString).toLocaleString();
    } catch {
      return isoString;
    }
  }

  function renderHistory(items) {
    historyList.innerHTML = "";
    if (!items || items.length === 0) {
      historyList.innerHTML = '<div class="empty-state">No captions generated yet. Your history will appear here.</div>';
      return;
    }

    items.forEach((item) => {
      const row = document.createElement("div");
      row.className = "history-item";
      row.innerHTML = `
        <div class="history-item__body">
          <p class="history-item__caption">${escapeHtml(item.caption)}</p>
          <div class="history-item__meta">
            <span>${escapeHtml(item.filename)}</span>
            <span>${item.mode}</span>
            <span>${formatDate(item.created_at)}</span>
          </div>
        </div>
        <div class="history-item__actions">
          <button class="icon-btn" title="Download" data-download="${item.id}">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v12M6 11l6 6 6-6"/><path d="M5 21h14"/></svg>
          </button>
          <button class="icon-btn" title="Delete" data-delete="${item.id}">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2m-8 0v13a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2V7"/></svg>
          </button>
        </div>
      `;
      historyList.appendChild(row);
    });

    historyList.querySelectorAll("[data-download]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = btn.getAttribute("data-download");
        window.location.href = `/api/history/${id}/download`;
      });
    });

    historyList.querySelectorAll("[data-delete]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const id = btn.getAttribute("data-delete");
        const response = await fetch(`/api/history/${id}`, { method: "DELETE" });
        if (response.ok) {
          showToast("History item deleted.");
          loadHistory();
        } else {
          showToast("Could not delete history item.");
        }
      });
    });
  }

  function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value ?? "";
    return div.innerHTML;
  }

  async function loadHistory() {
    try {
      const response = await fetch("/api/history?limit=20&offset=0");
      if (!response.ok) return;
      const data = await response.json();
      renderHistory(data.items);
    } catch {
      /* silent: history is a non-critical enhancement */
    }
  }

  refreshHistoryBtn.addEventListener("click", loadHistory);

  // ---------------------------------------------------------------------
  // Health check on load
  // ---------------------------------------------------------------------
  async function checkHealth() {
    try {
      const response = await fetch("/api/health");
      const data = await response.json();
      if (!data.configured) {
        showBanner(
          "The server is missing an OPENAI_API_KEY. Add one to your .env file and restart the app to generate captions."
        );
      }
    } catch {
      showBanner("Could not reach the server. Confirm the application is running.");
    }
  }

  // ---------------------------------------------------------------------
  // Init
  // ---------------------------------------------------------------------
  initTheme();
  checkHealth();
  loadHistory();
})();
