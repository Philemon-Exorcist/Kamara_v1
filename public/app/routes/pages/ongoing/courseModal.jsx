
import { ImagePlus, LoaderCircle, Send, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

export default function CourseModal({ course, errorMessage, isLoading = false, isOpen, onClose, onSubmit }) {
  const [prompt, setPrompt] = useState("");
  const [photos, setPhotos] = useState([]);

  useEffect(() => {
    if (!isOpen) {
      setPrompt("");
      setPhotos([]);
    }
  }, [isOpen]);

  const previews = useMemo(
    () =>
      photos.map((photo) => ({
        name: photo.name,
        url: URL.createObjectURL(photo),
      })),
    [photos]
  );

  useEffect(() => {
    return () => {
      previews.forEach((preview) => URL.revokeObjectURL(preview.url));
    };
  }, [previews]);

  if (!isOpen || !course) {
    return null;
  }

  const handlePhotoChange = (event) => {
    const selectedPhotos = Array.from(event.target.files || []);
    setPhotos((currentPhotos) => [...currentPhotos, ...selectedPhotos]);
    event.target.value = "";
  };

  const handleRemovePhoto = (photoName) => {
    setPhotos((currentPhotos) => currentPhotos.filter((photo) => photo.name !== photoName));
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    if (!prompt.trim() && photos.length === 0) {
      return;
    }

    onSubmit?.({
      course,
      prompt: prompt.trim(),
      photos,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 px-4 py-6" role="dialog" aria-modal="true" aria-labelledby="course-modal-title">
      <div className="w-full max-w-2xl rounded-lg bg-white shadow-2xl">
        <div className="flex items-start justify-between gap-4 border-b border-slate-200 px-6 py-5">
          <div>
            <p className="text-sm font-medium text-blue-600">Create course request</p>
            <h2 id="course-modal-title" className="mt-1 text-2xl font-bold text-slate-900">
              {course.title}
            </h2>
            <p className="mt-1 text-sm text-slate-600">{course.description}</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            disabled={isLoading}
            className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-slate-500 transition hover:bg-slate-100 hover:text-slate-900"
            aria-label="Close course modal"
          >
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5 px-6 py-5">
          <label className="block">
            <span className="text-sm font-semibold text-slate-800">Prompt</span>
            <textarea
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              disabled={isLoading}
              rows={6}
              placeholder="Tell Kamara what you want to learn, revise, summarize, or generate for this course."
              className="mt-2 w-full resize-none rounded-lg border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
            />
          </label>

          <div>
            <label
              htmlFor="course-photo-upload"
              className="flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-slate-300 bg-slate-50 px-4 py-6 text-center transition hover:border-blue-400 hover:bg-blue-50"
            >
              <ImagePlus className="text-blue-600" size={28} />
              <span className="mt-3 text-sm font-semibold text-slate-800">Add photos</span>
              <span className="mt-1 text-xs text-slate-500">Upload notes, textbook pages, diagrams, or screenshots.</span>
              <input id="course-photo-upload" type="file" accept="image/*" multiple onChange={handlePhotoChange} disabled={isLoading} className="sr-only" />
            </label>

            {previews.length > 0 && (
              <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
                {previews.map((preview) => (
                  <div key={preview.name} className="relative overflow-hidden rounded-lg border border-slate-200 bg-slate-100">
                    <img src={preview.url} alt={preview.name} className="h-28 w-full object-cover" />
                    <button
                      type="button"
                      onClick={() => handleRemovePhoto(preview.name)}
                      disabled={isLoading}
                      className="absolute right-2 top-2 inline-flex h-7 w-7 items-center justify-center rounded-full bg-white/95 text-slate-700 shadow-sm transition hover:bg-slate-900 hover:text-white"
                      aria-label={`Remove ${preview.name}`}
                    >
                      <X size={14} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {errorMessage && (
            <p className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
              {errorMessage}
            </p>
          )}

          <div className="flex flex-col-reverse gap-3 border-t border-slate-200 pt-5 sm:flex-row sm:justify-end">
            <button type="button" onClick={onClose} disabled={isLoading} className="rounded-lg border border-slate-300 px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60">
              Cancel
            </button>
            <button type="submit" disabled={isLoading} className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400">
              {isLoading ? <LoaderCircle size={16} className="animate-spin" /> : <Send size={16} />}
              {isLoading ? "Sending..." : "Submit prompt"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
