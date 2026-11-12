import { useState } from "react";

export default function QuestionComposer({ onSend, disabled, isSending }) {
  const [text, setText] = useState("");
  function submit(e) {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    onSend(text);
    setText("");
  }
  return (
    <form onSubmit={submit} className="flex gap-2 border-t border-slate-800 p-3">
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={disabled}
        placeholder={disabled && !isSending ? "Available once processing finishes" : "Ask about the video…"}
        className="flex-1 rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-indigo-400 disabled:opacity-50"
      />
      <button disabled={disabled || !text.trim()} className="rounded-lg bg-indigo-500 px-4 py-2 text-sm font-medium hover:bg-indigo-400 disabled:opacity-40">
        {isSending ? "…" : "Ask"}
      </button>
    </form>
  );
}
