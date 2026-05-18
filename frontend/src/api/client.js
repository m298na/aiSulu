const JSON_HEADERS = {
  "Content-Type": "application/json",
};

async function request(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    let message = "Request failed";
    try {
      const payload = await response.json();
      message = payload.detail || message;
    } catch {
      message = response.statusText || message;
    }
    throw new Error(message);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export function askQuestion(payload) {
  return request("/api/chat/ask", {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify(payload),
  });
}

export function transcribeAudio() {
  const formData = new FormData();
  return request("/api/chat/transcribe", {
    method: "POST",
    body: formData,
  });
}

export function synthesizeSpeech(text) {
  return request("/api/chat/speak", {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify({ text }),
  });
}

export function getKnowledgeFaqs() {
  return request("/api/knowledge-base/faqs");
}

export function searchKnowledgeBase(query) {
  return request(`/api/knowledge-base/search?q=${encodeURIComponent(query)}`);
}

export function getAdminStatus() {
  return request("/api/admin/status");
}

export function getAdminFaqs() {
  return request("/api/admin/faqs");
}

export function createFaq(payload) {
  return request("/api/admin/faqs", {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify(payload),
  });
}

export function updateFaq(id, payload) {
  return request(`/api/admin/faqs/${id}`, {
    method: "PUT",
    headers: JSON_HEADERS,
    body: JSON.stringify(payload),
  });
}

export function deleteFaq(id) {
  return request(`/api/admin/faqs/${id}`, {
    method: "DELETE",
  });
}

export function reloadKnowledgeBase() {
  return request("/api/admin/knowledge-base/reload", {
    method: "POST",
  });
}

export function getQuestionLogs() {
  return request("/api/logs/questions?limit=100");
}

export function getLogsStats() {
  return request("/api/logs/stats");
}
