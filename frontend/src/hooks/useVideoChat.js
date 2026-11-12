import { useRef, useState } from "react";
import { askQuestion } from "../services/api";

export function useVideoChat(videoId) {
  const [messages, setMessages] = useState([]);
  const [isSending, setIsSending] = useState(false);
  const conversationId = useRef(crypto.randomUUID());

  async function send(question) {
    const q = question.trim();
    if (!q || isSending) return;
    const add = (m) => setMessages((prev) => [...prev, { id: crypto.randomUUID(), createdAt: Date.now(), evidence: [], ...m }]);
    add({ role: "user", content: q });
    setIsSending(true);
    try {
      const res = await askQuestion(videoId, q, conversationId.current);
      add({
        role: "assistant",
        content: res.answer,
        status: res.status,
        evidence: res.evidence.map((e) => ({ chunkId: e.chunk_id, start: e.start_seconds, end: e.end_seconds, text: e.text })),
        frames: (res.visual_evidence || []).map((f) => ({
          frameId: f.frame_id, timestamp: f.timestamp_seconds, match: f.match, text: f.nearby_text,
        })),
      });
    } catch (e) {
      add({ role: "assistant", content: e.message, status: "error" });
    } finally {
      setIsSending(false);
    }
  }

  return { messages, isSending, send };
}
