import { DashboardSidebar, DashboardTopbar } from ".";
import { BookOpen } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { dashboardApi, type DashboardSession } from "../dashboard-api";
import { ProtectedGate } from "../../auth/protected-gate";

export function meta() {
  return [
    { title: "Recent Sessions | Kamara AI" },
    {
      name: "description",
      content: "Access your recently viewed sessions.",
    },
  ];
}

export default function RecentSessionsPage() {
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [sessions, setSessions] = useState<DashboardSession[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    let ignore = false;

    dashboardApi
      .getSessions()
      .then((data) => {
        if (!ignore) {
          setSessions(data.sessions);
          setError("");
        }
      })
      .catch((loadError) => {
        if (!ignore) {
          setError(loadError instanceof Error ? loadError.message : "Could not load your recent sessions.");
        }
      });

    return () => {
      ignore = true;
    };
  }, []);

  const filteredCourses = useMemo(() => {
    if (!searchQuery) {
      return sessions;
    }
    return sessions.filter(
      (course) =>
        getSessionTitle(course).toLowerCase().includes(searchQuery.toLowerCase()) ||
        getSessionDescription(course).toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [searchQuery, sessions]);

  return (
    <ProtectedGate>
      <main className="min-h-screen bg-slate-100 text-slate-900">
        <DashboardSidebar isOpen={isSidebarOpen} onClose={() => setSidebarOpen(false)} />
        <section className="md:ml-[300px] min-h-screen" aria-label="Recent Sessions">
          <DashboardTopbar onMenuClick={() => setSidebarOpen(true)} onSearchChange={setSearchQuery} />
          <div className="p-6">
            <h1 className="text-3xl font-bold text-slate-900 mb-6">Recent Sessions</h1>
            {error ? (
              <div className="mb-6 rounded-3xl border border-red-200 bg-red-50 px-5 py-4 text-sm font-medium text-red-700">
                {error}
              </div>
            ) : null}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredCourses.map((course) => (
                <div key={course.id} className="bg-white rounded-lg shadow-md p-6 flex flex-col justify-between hover:shadow-lg transition-shadow">
                  <div>
                    <div className="text-blue-600 mb-4">
                      <BookOpen size={24} />
                    </div>
                    <h2 className="text-lg font-semibold text-slate-800 mb-2">{getSessionTitle(course)}</h2>
                    <p className="text-sm text-slate-600 mb-4">{getSessionDescription(course)}</p>
                    {course.created_at ? <p className="text-xs text-slate-500 mb-4">Started {formatDate(course.created_at)}</p> : null}
                  </div>
                  <a href="/ongoing/learning" className="text-sm font-semibold text-blue-600 hover:text-blue-700 self-start">
                    Continue Learning &rarr;
                  </a>
                </div>
              ))}
              {filteredCourses.length === 0 && (
                <div className="col-span-full text-center py-12 text-slate-500">
                  <p className="text-lg font-semibold">No sessions found</p>
                  <p>Try adjusting your search query.</p>
                </div>
              )}
            </div>
          </div>
        </section>
      </main>
    </ProtectedGate>
  );
}

function getSessionTitle(session: DashboardSession) {
  return session.topic || session.user_prompt || session.course || session.subject || "Untitled session";
}

function getSessionDescription(session: DashboardSession) {
  const subject = session.subject || session.course || "Learning session";
  const status = session.is_active ? "Active" : "Saved";
  return `${status} ${subject} workspace.`;
}

function formatDate(date: string) {
  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
  }).format(new Date(date));
}
