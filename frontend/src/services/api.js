const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

async function errorFrom(res) {
  try {
    const body = await res.json();
    return body.detail || `Request failed (${res.status})`;
  } catch {
    return `Request failed (${res.status})`;
  }
}

export const videoFileUrl = (id) => `${BASE}/videos/${id}/file`;
export const frameUrl = (id, frameId) => `${BASE}/videos/${id}/frames/${frameId}.jpg`;

export async function getConfig() {
  const res = await fetch(`${BASE}/config`);
  if (!res.ok) throw new Error(await errorFrom(res));
  return res.json();
}

// XHR so we get upload progress events.
export function uploadVideo(file, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${BASE}/videos`);
    xhr.upload.onprogress = (e) => e.lengthComputable && onProgress(Math.round((e.loaded / e.total) * 100));
    xhr.onload = () => {
      let body = {};
      try { body = JSON.parse(xhr.responseText); } catch {}
      if (xhr.status >= 200 && xhr.status < 300) resolve(body);
      else reject(new Error(body.detail || `Upload failed (${xhr.status})`));
    };
    xhr.onerror = () => reject(new Error("Could not reach the server"));
    const form = new FormData();
    form.append("file", file);
    xhr.send(form);
  });
}

export async function getStatus(id) {
  const res = await fetch(`${BASE}/videos/${id}/status`);
  if (!res.ok) throw new Error(await errorFrom(res));
  return res.json();
}

export async function askQuestion(id, question, conversationId) {
  const res = await fetch(`${BASE}/videos/${id}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, conversation_id: conversationId }),
  });
  if (!res.ok) throw new Error(await errorFrom(res));
  return res.json();
}

export async function deleteVideo(id) {
  await fetch(`${BASE}/videos/${id}`, { method: "DELETE" });
}
