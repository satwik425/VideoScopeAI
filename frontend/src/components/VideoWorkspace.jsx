import { useRef } from "react";
import { videoFileUrl } from "../services/api";
import { useVideoChat } from "../hooks/useVideoChat";
import { formatTime } from "../utils/formatTime";
import ChatInterface from "./ChatInterface";
import ProcessingStatus from "./ProcessingStatus";
import VideoPlayer from "./VideoPlayer";

export default function VideoWorkspace({ video, processing }) {
  const player = useRef(null);
  const { messages, isSending, send } = useVideoChat(video.id);

  return (
    <main className="grid min-h-0 flex-1 gap-4 p-4 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
      <div className="space-y-3 lg:overflow-y-auto">
        <VideoPlayer ref={player} src={video.localUrl || videoFileUrl(video.id)} />
        <div>
          <h2 className="truncate font-medium">{video.filename}</h2>
          {video.durationSeconds ? <p className="text-xs text-slate-500">{formatTime(video.durationSeconds)}</p> : null}
        </div>
        <ProcessingStatus {...processing} />
      </div>
      <div className="flex min-h-[28rem] flex-col lg:min-h-0">
        <ChatInterface
          messages={messages}
          isSending={isSending}
          ready={processing.status === "ready"}
          videoId={video.id}
          onSend={send}
          onSeek={(s) => player.current?.seekTo(s)}
        />
      </div>
    </main>
  );
}
