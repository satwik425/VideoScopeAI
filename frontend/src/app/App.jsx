import { useEffect, useState } from "react";
import TopBar from "../components/TopBar";
import VideoUpload from "../components/VideoUpload";
import VideoWorkspace from "../components/VideoWorkspace";
import { useProcessingStatus } from "../hooks/useProcessingStatus";
import { useVideoUpload } from "../hooks/useVideoUpload";
import { deleteVideo } from "../services/api";

export default function App() {
  const [video, setVideo] = useState(null);
  const { upload, progress, uploading, error } = useVideoUpload();
  const processing = useProcessingStatus(video?.id);

  useEffect(() => () => video?.localUrl && URL.revokeObjectURL(video.localUrl), [video]);

  async function handleSelect(file) {
    const res = await upload(file);
    if (res) setVideo({ id: res.video_id, filename: res.filename, localUrl: URL.createObjectURL(file) });
  }

  async function reset() {
    if (video) await deleteVideo(video.id);
    setVideo(null);
  }

  return (
    <div className="flex h-full flex-col">
      <TopBar status={video ? processing.status : null} hasVideo={!!video} onReset={reset} />
      {video ? (
        <VideoWorkspace video={video} processing={processing} />
      ) : (
        <VideoUpload onSelect={handleSelect} uploading={uploading} progress={progress} error={error} />
      )}
    </div>
  );
}
