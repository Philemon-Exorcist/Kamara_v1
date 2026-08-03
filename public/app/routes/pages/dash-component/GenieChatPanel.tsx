import { Paperclip, Send, Sparkles, X, FileText } from "lucide-react";
import { useRef, useState } from "react";

interface GenieChatPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export function GenieChatPanel({ isOpen, onClose }: GenieChatPanelProps) {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [attachments, setAttachments] = useState<File[]>([]);

  const handleAttachmentClick = () => {
    fileInputRef.current?.click();
  };

  const handleAttachmentChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files ?? []);
    if (files.length > 0) {
      setAttachments((current) => [...current, ...files]);
      event.target.value = "";
    }
  };

  return (
    <aside
      className={`fixed right-0 top-0 z-30 hidden h-screen w-[420px] border-l border-blue-100 bg-white shadow-[-20px_0_60px_rgba(15,23,42,0.12)] transition-transform duration-300 md:block ${
        isOpen ? "translate-x-0" : "translate-x-full"
      }`}
      aria-label="Genie chat panel"
    >
      <div className="flex h-full flex-col bg-[radial-gradient(circle_at_top,_rgba(37,99,235,0.08),_transparent_34%),linear-gradient(180deg,_#ffffff_0%,_#f8fbff_100%)]">
        <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">AI assistant</h2>
            <p className="text-sm text-slate-500">Ask Genie to build, explain, or guide.</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 text-slate-600 transition hover:bg-blue-50 hover:text-blue-700"
            aria-label="Close Genie panel"
          >
            <X size={18} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-6">
          <div className="mx-auto flex max-w-md flex-col items-center gap-5 text-center">
            <div className="flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-blue-600 via-blue-500 to-cyan-400 shadow-[0_18px_40px_rgba(37,99,235,0.28)]">
              <Sparkles size={34} className="text-white" />
            </div>
            <div>
              <p className="text-lg font-semibold text-slate-900">Good morning, are you ready for classes?</p>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                Tell Genie what you want to learn, and it will help you create a focused session.
              </p>
            </div>
          </div>
        </div>

        <div className="border-t border-slate-200 bg-white/90 p-4 backdrop-blur">
          <div className="rounded-[24px] border border-slate-200 bg-white p-3 shadow-sm">
            <input ref={fileInputRef} type="file" multiple className="hidden" onChange={handleAttachmentChange} />
            <textarea rows={3} placeholder="Write your answer..." className="w-full resize-none bg-transparent text-sm outline-none placeholder:text-slate-400" />

            {attachments.length > 0 ? (
              <div className="mt-3 flex flex-wrap gap-2">
                {attachments.map((file) => (
                  <span
                    key={`${file.name}-${file.lastModified}`}
                    className="inline-flex items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-3 py-1.5 text-xs font-medium text-blue-700"
                  >
                    <FileText size={12} />
                    {file.name}
                  </span>
                ))}
              </div>
            ) : null}

            <div className="mt-3 flex items-center justify-between gap-3">
              <button
                type="button"
                onClick={handleAttachmentClick}
                className="inline-flex items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700 transition hover:bg-blue-100"
              >
                <Paperclip size={16} />
                Attachments
              </button>
              <div className="flex items-center gap-3">
                <button type="button" className="inline-flex items-center gap-2 rounded-full bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700">
                  Deploy Genie
                </button>
                <button
                  type="button"
                  className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-slate-600 transition hover:bg-blue-50 hover:text-blue-700"
                  aria-label="Send message"
                >
                  <Send size={16} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
