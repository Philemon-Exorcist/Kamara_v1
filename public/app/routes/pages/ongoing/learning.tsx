import { useEffect, useState, useRef, type FormEvent } from "react";
import {
  Award,
  BookOpen,
  ChevronDown,
  ChevronRight,
  Crown,
  FileBadge,
  Home,
  LibraryBig,
  LoaderCircle,
  Phone,
  PhoneOff,
  PanelRightClose,
  PanelRightOpen,
  Play,
  Mic,
  Send,
  Share2,
  Star,
  UserRound,
  Video,
  MicOff,
} from "lucide-react";
import { type Editor, serializeTldrawJson } from "tldraw";

import TldrawComponent from "../dash-component/tldraw";
import ModuleLibrary, { buildModulesFromBackendResponse, placeholderModules, type LearningModule } from "../dash-component/mod-lib";
import { getGeneratedCourseStorageKey } from "../course-api";

type GeneratedCourseSession = {
  session_id?: string;
  course?: {
    title?: string;
    description?: string;
  };
  prompt?: string;
  generatedCourse?: any;
};

type TutorEvent = {
  type: string;
  title: string;
  detail?: string;
};

const fallbackModules = placeholderModules;

const WS_BASE_URL =
  typeof window !== "undefined" && window.location.hostname === "localhost"
    ? "ws://localhost:8001/ws/api/v1"
    : "wss://kamara-v0-1.onrender.com/ws/api/v1";
const COURSE_MODULES_WS_ENDPOINT = `${WS_BASE_URL}/courses/hrm/modules`;

function isAudioStreamingSupported() {
  return typeof window !== "undefined" && "MediaRecorder" in window && "WebSocket" in window;
}

function getActiveSessionId() {
  if (typeof window === "undefined") {
    return null;
  }

  const params = new URLSearchParams(window.location.search);
  return params.get("session_id") ?? localStorage.getItem("active_session_id") ?? getStoredGeneratedSessionId();
}

function getGeneratedSessionId(generatedSession: GeneratedCourseSession | null) {
  const generatedCourse = generatedSession?.generatedCourse;

  return (
    generatedCourse?.session_id ??
    generatedCourse?.data?.session_id ??
    generatedCourse?.id ??
    generatedSession?.session_id ??
    null
  );
}

function getStoredGeneratedSessionId() {
  if (typeof window === "undefined") {
    return null;
  }

  const storageKey = getGeneratedCourseStorageKey();
  const storedCourse = sessionStorage.getItem(storageKey);

  if (!storedCourse) {
    return null;
  }

  try {
    const parsedCourse = JSON.parse(storedCourse) as GeneratedCourseSession;
    return getGeneratedSessionId(parsedCourse);
  } catch {
    return null;
  }
}

export function meta() {
  return [
    { title: "Learning | Kamara AI" },
    {
      name: "description",
      content: "Course progress .",
    },
  ];
}

export default function DashboardPage() {
  const [modules, setModules] = useState<LearningModule[]>(fallbackModules);
  const [generatedSession, setGeneratedSession] = useState<GeneratedCourseSession | null>(null);
  const [selectedModuleId, setSelectedModuleId] = useState(fallbackModules[0]?.id ?? "");
  const [chatInput, setChatInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [isMicConnecting, setIsMicConnecting] = useState(false);
  const [isTutorConnected, setIsTutorConnected] = useState(false);
  const [isTutorConnecting, setIsTutorConnecting] = useState(false);
  const [isLearningPanelOpen, setIsLearningPanelOpen] = useState(true);
  const [isLibraryOpen, setIsLibraryOpen] = useState(false);
  const [boardEditor, setBoardEditor] = useState<Editor | null>(null);
  const [tutorEvents, setTutorEvents] = useState<TutorEvent[]>([]);

  const moduleSocketRef = useRef<WebSocket | null>(null);
  const tutorSocketRef = useRef<WebSocket | null>(null);
  const audioStreamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const audioSourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const audioProcessorRef = useRef<ScriptProcessorNode | null>(null);
  const boardSnapshotTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    const storageKey = getGeneratedCourseStorageKey();
    const storedCourse = sessionStorage.getItem(storageKey);

    if (!storedCourse) {
      return;
    }

    try {
      const parsedCourse = JSON.parse(storedCourse) as GeneratedCourseSession;
      const generatedModules = buildModulesFromBackendResponse(parsedCourse.generatedCourse);
      const sessionId = getGeneratedSessionId(parsedCourse);

      setGeneratedSession(parsedCourse);

      if (sessionId) {
        localStorage.setItem("active_session_id", String(sessionId));
      }

      if (generatedModules.length > 0) {
        setModules(generatedModules);
        setSelectedModuleId(generatedModules[0].id);
      }
    } catch {
      sessionStorage.removeItem(storageKey);
    }
  }, []);

  useEffect(() => {
    if (generatedSession) {
      return;
    }

    moduleSocketRef.current = new WebSocket(COURSE_MODULES_WS_ENDPOINT);
    const currentSocket = moduleSocketRef.current;

    currentSocket.addEventListener("open", () => {
      currentSocket.send(JSON.stringify({ action: "get_modules" }));
    });

    currentSocket.addEventListener("message", (event) => {
      try {
        const payload = JSON.parse(event.data);

        if (payload.type === "course_modules" && Array.isArray(payload.modules)) {
          const backendModules = buildModulesFromBackendResponse(payload);
          setModules(backendModules);
          setSelectedModuleId(backendModules[0]?.id ?? "");
        }

        if (payload.type === "chat_response") {
          // You can handle chat responses from the backend here
          console.log("AI Response:", payload.content);
        }
      } catch {
        setModules(fallbackModules);
        setSelectedModuleId(fallbackModules[0]?.id ?? "");
      }
    });

    currentSocket.addEventListener("error", () => {
      setModules(fallbackModules);
      setSelectedModuleId(fallbackModules[0]?.id ?? "");
    });

    return () => {
      if (currentSocket.readyState === WebSocket.OPEN) {
        currentSocket.send(JSON.stringify({ action: "close" }));
      }
      currentSocket.close();
    };
  }, [generatedSession]);

  const clearBoardSnapshotTimer = () => {
    if (boardSnapshotTimerRef.current) {
      clearTimeout(boardSnapshotTimerRef.current);
      boardSnapshotTimerRef.current = null;
    }
  };

  const pushTutorEvent = (event: TutorEvent) => {
    setTutorEvents((current) => [event, ...current].slice(0, 8));
  };

  const stopMicStream = () => {
    audioProcessorRef.current?.disconnect();
    audioSourceRef.current?.disconnect();
    audioContextRef.current?.close().catch(() => undefined);

    audioProcessorRef.current = null;
    audioSourceRef.current = null;
    audioContextRef.current = null;

    audioStreamRef.current?.getTracks().forEach((track) => track.stop());
    audioStreamRef.current = null;

    setIsRecording(false);
    setIsMicConnecting(false);
  };

  const disconnectTutorSession = () => {
    clearBoardSnapshotTimer();
    stopMicStream();

    const socket = tutorSocketRef.current;
    tutorSocketRef.current = null;
    setIsTutorConnected(false);
    setIsTutorConnecting(false);

    if (socket && socket.readyState !== WebSocket.CLOSED) {
      socket.close();
    }
  };

  const sendBoardSnapshot = async () => {
    const socket = tutorSocketRef.current;

    if (!boardEditor || !socket || socket.readyState !== WebSocket.OPEN) {
      return;
    }

    try {
      const snapshot = await serializeTldrawJson(boardEditor);

      socket.send(
        JSON.stringify({
          action: "board_snapshot",
          snapshot,
        })
      );
    } catch (error) {
      console.error("Could not serialize board snapshot:", error);
    }
  };

  const scheduleBoardSnapshot = () => {
    if (!isTutorConnected) {
      return;
    }

    clearBoardSnapshotTimer();
    boardSnapshotTimerRef.current = setTimeout(() => {
      void sendBoardSnapshot();
    }, 900);
  };

  const connectTutorSession = async () => {
    if (typeof window === "undefined" || !("WebSocket" in window)) {
      alert("Your browser does not support WebSocket streaming.");
      return false;
    }

    const token = localStorage.getItem("access_token");
    const sessionId = getGeneratedSessionId(generatedSession) ?? getActiveSessionId() ?? getStoredGeneratedSessionId();

    if (!token) {
      alert("Please sign in again to start the tutor call.");
      return false;
    }

    if (!sessionId) {
      alert("No active classroom session was found.");
      return false;
    }

    if (tutorSocketRef.current?.readyState === WebSocket.OPEN) {
      return true;
    }

    if (tutorSocketRef.current?.readyState === WebSocket.CONNECTING) {
      return true;
    }

    setIsTutorConnecting(true);

    return await new Promise<boolean>((resolve) => {
      const socket = new WebSocket(`${WS_BASE_URL}/live?token=${encodeURIComponent(token)}`);
      tutorSocketRef.current = socket;

      socket.onopen = () => {
        setIsTutorConnected(true);
        setIsTutorConnecting(false);

        socket.send(
          JSON.stringify({
            action: "start_session",
            session_id: sessionId,
          })
        );

        void sendBoardSnapshot();
        resolve(true);
      };

      socket.onmessage = (event) => {
        if (typeof event.data !== "string") {
          return;
        }

        try {
          const payload = JSON.parse(event.data);

          if (payload.type === "system_status") {
            pushTutorEvent({ type: payload.type, title: payload.content });
            console.log(payload.content);
            return;
          }

          if (payload.type === "system_error") {
            pushTutorEvent({
              type: payload.type,
              title: payload.content ?? "Tutor engine error",
              detail: payload.detail,
            });
            disconnectTutorSession();
            return;
          }

          if (payload.type === "assistant_text") {
            pushTutorEvent({
              type: payload.type,
              title: "Tutor said something",
              detail: payload.content,
            });
            return;
          }

          if (payload.type === "tool_call") {
            pushTutorEvent({
              type: payload.type,
              title: `Tool call: ${payload.name}`,
              detail: JSON.stringify(payload.args ?? {}),
            });
            return;
          }

          if (payload.type === "tool_result") {
            pushTutorEvent({
              type: payload.type,
              title: `Tool result: ${payload.name}`,
              detail: JSON.stringify(payload.result ?? {}),
            });
            return;
          }
        } catch {
          pushTutorEvent({
            type: "message",
            title: "Tutor message",
            detail: event.data,
          });
        }
      };

      socket.onerror = () => {
        console.error("Tutor websocket error.");
        disconnectTutorSession();
        resolve(false);
      };

      socket.onclose = () => {
        clearBoardSnapshotTimer();
        stopMicStream();

        if (tutorSocketRef.current === socket) {
          tutorSocketRef.current = null;
        }

        setIsTutorConnected(false);
        setIsTutorConnecting(false);
      };
    });
  };

  useEffect(() => {
    if (!boardEditor || !isTutorConnected) {
      return;
    }

    const removeListener = boardEditor.store.listen(
      () => {
        scheduleBoardSnapshot();
      },
      {
        source: "user",
        scope: "document",
      }
    );

    void sendBoardSnapshot();

    return () => {
      removeListener();
      clearBoardSnapshotTimer();
    };
  }, [boardEditor, isTutorConnected]);

  useEffect(() => {
    return () => {
      disconnectTutorSession();
      if (moduleSocketRef.current?.readyState === WebSocket.OPEN) {
        moduleSocketRef.current.send(JSON.stringify({ action: "close" }));
      }
      moduleSocketRef.current?.close();
    };
  }, []);

  const handleMicToggle = async () => {
    if (!isAudioStreamingSupported()) {
      alert("Your browser does not support audio streaming.");
      return;
    }

    if (isRecording || isMicConnecting) {
      stopMicStream();
      return;
    }

    const tutorReady = await connectTutorSession();
    if (!tutorReady || tutorSocketRef.current?.readyState !== WebSocket.OPEN) {
      return;
    }

    setIsMicConnecting(true);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioStreamRef.current = stream;

      const socket = tutorSocketRef.current;

      if (!socket || socket.readyState !== WebSocket.OPEN) {
        stopMicStream();
        return;
      }

      const audioContext = new AudioContext({ sampleRate: 16000 });
      const source = audioContext.createMediaStreamSource(stream);
      const processor = audioContext.createScriptProcessor(4096, 1, 1);

      const floatTo16BitPCM = (input: Float32Array) => {
        const buffer = new ArrayBuffer(input.length * 2);
        const view = new DataView(buffer);

        for (let i = 0; i < input.length; i += 1) {
          const sample = Math.max(-1, Math.min(1, input[i] ?? 0));
          view.setInt16(i * 2, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true);
        }

        return buffer;
      };

      processor.onaudioprocess = (event) => {
        if (socket.readyState !== WebSocket.OPEN) {
          return;
        }

        const input = event.inputBuffer.getChannelData(0);
        socket.send(floatTo16BitPCM(input));
      };

      source.connect(processor);
      processor.connect(audioContext.destination);

      audioContextRef.current = audioContext;
      audioSourceRef.current = source;
      audioProcessorRef.current = processor;

      setIsRecording(true);
      setIsMicConnecting(false);
    } catch (error) {
      console.error("Could not get microphone access:", error);
      stopMicStream();
      alert("Could not access your microphone. Please check your browser permissions.");
    }
  };

  const handleTutorToggle = async () => {
    if (isTutorConnected || isTutorConnecting) {
      disconnectTutorSession();
      return;
    }

    await connectTutorSession();
  };

  const handleChatSubmit = (e: FormEvent) => {
    e.preventDefault();
    const message = chatInput.trim();
    if (!message || !moduleSocketRef.current || moduleSocketRef.current.readyState !== WebSocket.OPEN) {
      return;
    }

    moduleSocketRef.current.send(JSON.stringify({ type: "chat_message", content: message }));
    setChatInput("");
  };

  const generatedCourse = generatedSession?.generatedCourse;
  const courseTitle = generatedSession?.course?.title ?? generatedCourse?.title ?? generatedCourse?.course_title ?? "Human Resource Management";
  const courseDescription = generatedSession?.course?.description ?? generatedCourse?.description;
  const generatedSummary = generatedCourse?.summary ?? generatedCourse?.content ?? generatedCourse?.message;
  const generatedFiles = Array.isArray(generatedCourse?.files)
    ? generatedCourse.files
    : Array.isArray(generatedCourse?.data?.files)
      ? generatedCourse.data.files
      : Array.isArray(generatedCourse?.resources)
        ? generatedCourse.resources
        : [];

  return (
    <main className="min-h-screen bg-white text-slate-900 p-6">
      <header className="flex flex-col md:flex-row items-start md:items-center justify-between border-b border-blue-100 pb-4 mb-6" aria-label="Course navigation">
        <nav className="flex flex-wrap items-center gap-4 mb-4 md:mb-0">
          <a href="/dashboard" className="text-sm font-semibold text-blue-700 inline-flex items-center gap-2">
            <Home size={15} aria-hidden="true" />
            Dashboard
          </a>
          <div className="text-blue-700 font-semibold " >Kamara </div>
        </nav>

        <div className="flex items-center gap-3 w-full md:w-auto">
          <button className="w-10 h-10 rounded-full bg-blue-50 text-blue-700 flex items-center justify-center" type="button" aria-label="Open profile">
            <UserRound size={20} aria-hidden="true" />
          </button>
        </div>
      </header>

      <section className="grid min-h-[calc(100vh-160px)] gap-4 xl:grid-cols-[minmax(0,1fr)_auto_auto]" aria-label="Learning workspace">
        <div className="min-w-0 overflow-hidden rounded-lg border border-blue-100 bg-white shadow-sm">
          <div className="border-b border-blue-100 p-5">
            <h1 className="text-2xl font-bold text-slate-900">{courseTitle}</h1>
            {courseDescription && <p className="mt-2 text-sm text-slate-600">{courseDescription}</p>}
            <div className="mt-3 inline-flex items-center gap-2 text-sm text-slate-600">
              <Video size={13} aria-hidden="true" className="text-blue-600" />
              {modules.length} modules
            </div>
          </div>

          <div className="h-[58vh] min-h-[420px]">
            <TldrawComponent sessionId={getGeneratedSessionId(generatedSession) ?? undefined} onEditorReady={setBoardEditor} />
          </div>

          <div className="border-t border-blue-100 p-4">
            <form onSubmit={handleChatSubmit} className="flex w-full items-center gap-2">
              <textarea
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Ask Kamara a question..."
                rows={1}
                className="flex-1 resize-none rounded-lg border border-slate-300 bg-slate-50 p-3 text-sm outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
              />
              <button type="submit" className="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-blue-600 text-white shadow-sm transition hover:bg-blue-700" aria-label="Send message">
                <Send size={18} />
              </button>
              <button
                type="button"
                onClick={handleTutorToggle}
                className={`inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-lg shadow-sm transition ${
                  isTutorConnected || isTutorConnecting ? "bg-blue-600 text-white hover:bg-blue-700" : "bg-slate-200 text-slate-700 hover:bg-slate-300"
                }`}
                aria-label={isTutorConnected || isTutorConnecting ? "Disconnect tutor call" : "Activate tutor call"}
                title={isTutorConnected || isTutorConnecting ? "Disconnect tutor call" : "Activate tutor call"}
              >
                {isTutorConnecting ? <LoaderCircle size={18} className="animate-spin" /> : isTutorConnected ? <PhoneOff size={18} /> : <Phone size={18} />}
              </button>
              <button
                type="button"
                onClick={handleMicToggle}
                className={`inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-lg shadow-sm transition ${
                  isRecording || isMicConnecting ? "bg-blue-600 text-white hover:bg-blue-700" : "bg-slate-200 text-slate-700 hover:bg-slate-300"
                }`}
                aria-label={isRecording || isMicConnecting ? "Turn microphone off" : "Turn microphone on"}
                title={isRecording || isMicConnecting ? "Turn microphone off" : "Turn microphone on"}
              >
                {isMicConnecting ? <LoaderCircle size={18} className="animate-spin" /> : isRecording ? <MicOff size={18} /> : <Mic size={18} />}
              </button>
            </form>
            {tutorEvents.length > 0 && (
              <div className="mt-3 rounded-lg border border-blue-100 bg-slate-50 p-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Tutor stream</h3>
                  <span className="text-xs text-slate-400">{isTutorConnected ? "Live" : "Offline"}</span>
                </div>
                <div className="mt-2 space-y-2">
                  {tutorEvents.map((event, index) => (
                    <div key={`${event.type}-${index}`} className="rounded-md bg-white p-2 text-sm text-slate-700 shadow-sm">
                      <div className="font-semibold text-slate-900">{event.title}</div>
                      {event.detail && <div className="mt-1 break-words text-xs text-slate-500">{event.detail}</div>}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {isLearningPanelOpen && (
          <aside className="max-h-[calc(100vh-160px)] w-full overflow-y-auto rounded-lg border border-blue-100 bg-white shadow-sm xl:w-[350px]" aria-label="Learning modules">
            <div className="sticky top-0 z-10 flex items-center justify-between border-b border-blue-100 bg-white px-5 py-4">
              <h2 className="text-base font-bold text-slate-900">Learning</h2>
              <button type="button" onClick={() => setIsLearningPanelOpen(false)} className="inline-flex h-9 w-9 items-center justify-center rounded-lg text-slate-600 transition hover:bg-slate-100 hover:text-slate-900" aria-label="Close learning panel">
                <PanelRightClose size={18} />
              </button>
            </div>

            <ModuleLibrary modules={modules} selectedModuleId={selectedModuleId} onModuleSelect={(module) => setSelectedModuleId(module.id)} />
          </aside>
        )}

        <aside className="flex flex-row gap-2 rounded-lg border border-blue-100 bg-white p-2 shadow-sm xl:flex-col" aria-label="Workspace tools">
          <button
            type="button"
            onClick={() => setIsLearningPanelOpen((isOpen) => !isOpen)}
            className="inline-flex h-11 w-11 items-center justify-center rounded-lg text-blue-700 transition hover:bg-blue-50"
            aria-label={isLearningPanelOpen ? "Close learning panel" : "Open learning panel"}
            title={isLearningPanelOpen ? "Close learning panel" : "Open learning panel"}
          >
            {isLearningPanelOpen ? <PanelRightClose size={19} /> : <PanelRightOpen size={19} />}
          </button>
          <button
            type="button"
            onClick={() => setIsLibraryOpen((isOpen) => !isOpen)}
            className={`inline-flex h-11 w-11 items-center justify-center rounded-lg transition ${isLibraryOpen ? "bg-blue-600 text-white" : "text-blue-700 hover:bg-blue-50"}`}
            aria-label="Open generated file library"
            title="Open generated file library"
          >
            <LibraryBig size={19} />
          </button>
        </aside>
      </section>

      {isLibraryOpen && (
        <section className="mt-4 rounded-lg border border-blue-100 bg-blue-50 p-4" aria-label="Generated file library">
          <div className="flex items-center justify-between gap-4">
            <h2 className="text-base font-bold text-slate-900">Generated file library</h2>
            <button type="button" onClick={() => setIsLibraryOpen(false)} className="text-sm font-semibold text-blue-700 hover:text-blue-800">
              Close
            </button>
          </div>

          {generatedFiles.length > 0 ? (
            <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {generatedFiles.map((file: any, index: number) => (
                <a key={String(file.id ?? file.url ?? index)} href={String(file.url ?? file.href ?? "#")} className="rounded-lg border border-blue-100 bg-white p-4 text-sm font-semibold text-slate-800 shadow-sm transition hover:border-blue-300 hover:text-blue-700">
                  {String(file.title ?? file.name ?? `Generated file ${index + 1}`)}
                </a>
              ))}
            </div>
          ) : (
            <p className="mt-3 text-sm text-slate-600">No generated files are available yet.</p>
          )}

          {(generatedSession?.prompt || generatedSummary) && (
            <div className="mt-4 rounded-lg border border-blue-100 bg-white p-4">
              {generatedSession?.prompt && (
                <div>
                  <h3 className="text-sm font-semibold text-slate-900">Your prompt</h3>
                  <p className="mt-1 text-sm text-slate-700">{generatedSession.prompt}</p>
                </div>
              )}
              {generatedSummary && (
                <div className="mt-4">
                  <h3 className="text-sm font-semibold text-slate-900">Backend response</h3>
                  <p className="mt-1 whitespace-pre-wrap text-sm text-slate-700">{String(generatedSummary)}</p>
                </div>
              )}
            </div>
          )}
        </section>
      )}
    </main>
  );
}
