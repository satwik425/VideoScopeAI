import { useEffect, useRef } from "react";
import ChatMessage from "./ChatMessage";
import QuestionComposer from "./QuestionComposer";
import SuggestedQuestions from "./SuggestedQuestions";

export default function ChatInterface({ messages, isSending, ready, videoId, onSend, onSeek }) {
  const end = useRef(null);
  useEffect(() => {
    end.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);

  return (
    <section className="flex min-h-0 flex-1 flex-col rounded-2xl border border-slate-800 bg-slate-900/50">
      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.length === 0 && (
          <div className="space-y-3">
            <p className="text-sm text-slate-400">Ask a question about what’s said in this video.</p>
            <SuggestedQuestions onPick={onSend} disabled={!ready || isSending} />
          </div>
        )}
        {messages.map((m) => <ChatMessage key={m.id} message={m} videoId={videoId} onSeek={onSeek} />)}
        {isSending && <p className="text-sm text-slate-500">Thinking…</p>}
        <div ref={end} />
      </div>
      <QuestionComposer onSend={onSend} disabled={!ready || isSending} isSending={isSending} />
    </section>
  );
}
